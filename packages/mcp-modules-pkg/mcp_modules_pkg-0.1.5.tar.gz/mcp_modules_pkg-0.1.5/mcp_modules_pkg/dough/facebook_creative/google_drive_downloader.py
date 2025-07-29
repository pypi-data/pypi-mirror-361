"""
이 소스파일은 구글 드라이브로부터 몇몇 조건들에 부합하는 파일들을 다운로드
받는 기능을 가진 GDriveDownloader 클래스를 가지고 있습니다.
"""
from __future__ import print_function
import io
import errno
import pickle
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CREDENTIAL_FILE_PATH = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), "credentials.json"
)
TOKEN_PICKLE_PATH = os.path.join(
    os.path.realpath(os.path.dirname(__file__)), "token.pickle"
)
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.appdata",
    "https://www.googleapis.com/auth/drive.photos.readonly",
]


class GDriveDownloader:
    """
    이 클래스는 구글 드라이브로부터 쿼리 조건을 포함시켜 파일과 폴더를 찾고,
    다운받게 도와줍니다.
    1. 파일이름 기준
    2. 폴더 이름 기준
    3. 파일 포맷 기준
    4. 혼합 기
    """

    creds = None
    service = None

    def __init__(self):
        if os.path.exists(TOKEN_PICKLE_PATH):
            with open(TOKEN_PICKLE_PATH, "rb") as token:
                self.creds = pickle.load(token)
        else:
            print("Create new session")

        if not os.path.exists(CREDENTIAL_FILE_PATH):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), CREDENTIAL_FILE_PATH
            )

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refresh credential")
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIAL_FILE_PATH, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                print("Create credential history")

            with open(TOKEN_PICKLE_PATH, "wb") as token:
                pickle.dump(self.creds, token)

        self.service = build("drive", "v3", credentials=self.creds)

    def find_directories_in_parent(self, parent_id):
        """
        특정 이름의 상위폴더를 가진 폴더들을 찾아줍니다.
        """
        query = (
            f"mimeType='{GDriveDownloader.MIMEType.DIR}' and '{parent_id}' in parents"
        )
        results = self.send_request(query)
        return results.get("files", [])

    def find_directories_by_name(self, pattern, parent_id=None):
        """
        특정 이름을 가진 폴더들을 찾아줍니다.
        """
        query = f"mimeType='{GDriveDownloader.MIMEType.DIR}' and {pattern}"
        if parent_id is not None:
            query += f" and '{parent_id}' in parents"

        query += " and trashed = false"

        results = self.send_request(query)
        return results.get("files", [])

    def find_files_by_name(self, pattern=None, parent_id=None, filetype=None):
        """
        특정 패턴을 이름으로 가진 파일들을 찾아줍니다.
        """
        if pattern is None:
            raise ValueError

        query = pattern

        if parent_id is not None:
            query += f" and '{parent_id}' in parents "

        if filetype is not None:
            query += f" and mimeType='{filetype}'"
        query += " and trashed = false"

        results = self.send_request(query)
        return results.get("files", [])

    def find_files_by_MIME(self, pattern=None, parent_id=None):
        """
        특정 파일 포맷을 모두 찾아줍니다.
        """
        if pattern is None:
            raise ValueError
        query = pattern
        if parent_id is not None:
            query += f" and '{parent_id}' in parents"
        query += " and trashed = false"
        result = self.send_request(query)
        return result.get("files", [])

    def send_request(self, query):
        """
        위의 메서드들을 통해 작성된 쿼리를 호출합니다.
        """
        results = (
            self.service.files()
            .list(
                q=query,  # pylint: disable=no-member
                fields="nextPageToken, files(id, name)",
                corpora="allDrives",
                includeItemsFromAllDrives="True",
                supportsAllDrives="True",
            )
            .execute()
        )
        return results

    def download_files(self, files_info, dest=None):
        """
        쿼리문을 통해 받아온 파일 정보를 파라미터로 전달해서
        파일들을 다운도르 받습니다.
        """
        for file_info in files_info:
            file_path = dest
            if file_path is None:
                file_path = file_info["name"]
            else:
                file_path = os.path.join(file_path, file_info["name"])

            print(f"{file_info['name']} ({file_info['id']})")
            request = self.service.files().get_media(
                fileId=file_info["id"]
            )  # pylint: disable=no-member
            file_header = io.FileIO(file_path, "wb")
            downloader = MediaIoBaseDownload(file_header, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")

    def download(self, parent_id, pattern, dest):
        """다운로드를 실제로 진행하는 메소드

        Args:
            parent_id (_type_): google drive id
            pattern (_type_): search pattern
            dest (_type_): 다운로드 위치
        """
        target_video_files = self.find_files_by_MIME(
            parent_id=parent_id, pattern=pattern
        )
        tmp_video_folder = dest
        if not os.path.exists(tmp_video_folder):
            os.makedirs(tmp_video_folder)
        self.download_files(target_video_files, tmp_video_folder)
        print(f"{len(target_video_files)} video files download complete")

    class Operator:  # pylint: disable=too-few-public-methods
        """
        google drive api에서 사용되는 query operator들입니다.
        """

        EQUAL = "="
        CONTAINS = "contains"
        NOTCONTAINS = "not contains"
        AND = "and"
        OR = "or"
        NOT = "not"
        HAS = "has"
        NOTEQUAL = "!="
        LESS = "<"
        LESSEQUAL = "<="
        GREATER = ">"
        GREATEREQUAL = ">="
        IN = "in"

    class MIMEType:  # pylint: disable=too-few-public-methods
        """
        파일 타입에 따른 MIME명명 규칙입니다.
        """

        VIDEO = "video/mp4"
        IMAGE_PNG = "image/png"
        IMAGE_JPG = "image/jpeg"
        CSV = "text/csv"
        ICON = "image/x-icon"
        JSON = "application/json"
        PDF = "application/pdf"
        ZIP = "application/zip"
        TXT = "text/plain"
        DIR = "application/vnd.google-apps.folder"
