# -*- coding: utf-8 -*-
import io
import os

from dough.google_api.google_api_with_service_accounts import GoogleApiWithServiceAccounts
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


# https://developers.google.com/drive/api/guides/enable-shareddrives?hl=ko
class GoogleDriveDownloader(GoogleApiWithServiceAccounts):
    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.appdata",
        "https://www.googleapis.com/auth/drive.photos.readonly",
    ]

    def __init__(self, impersonate):
        super().__init__(self.SCOPES, impersonate)
        self.service = super().get_service(api="drive", version="v3")
        print(self.service)

    def find_directories_in_parent(self, parent_id):
        """
        특정 이름의 상위폴더를 가진 폴더들을 찾아줍니다.
        """
        query = "mimeType='{0}' and '{1}' in parents".format(GoogleDriveDownloader.MIMEType.DIR, parent_id)
        results = self.send_request(query)
        return results.get("files", [])

    def find_directories_by_name(self, pattern, parent_id=None):
        """
        특정 이름을 가진 폴더들을 찾아줍니다.
        """
        query = "mimeType='{0}' and {1}".format(GoogleDriveDownloader.MIMEType.DIR, pattern)
        if parent_id is not None:
            query += " and '{0}' in parents".format(parent_id)

        query += " and trashed = false"
        print(query)
        results = self.send_request(query)
        print(results)
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
                q=query,
                fields="nextPageToken, files(id, name)",
                corpora="allDrives",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        return results

    def move_file_to_trash(self, file_id):
        """Moves a specified file to the trash on Google Drive.

        Args:
            file_id (str): The ID of the file to be trashed.

        Returns:
            dict: The API response that includes the updated file metadata.
        """
        body_value = {"trashed": True}
        return self.service.files().update(fileId=file_id, body=body_value, supportsAllDrives=True).execute()

    def get_file(self, file_id):
        """Retrieves metadata for a specified file from Google Drive.

        Args:
            file_id (str): The ID of the file to retrieve metadata for.

        Returns:
            dict: The file metadata.
        """
        return self.service.files().get(fileId=file_id, supportsAllDrives=True).execute()

    def upload_file_data(self, file_name, file_data, mimetype=None, parent_id=None):
        """Uploads file data to Google Drive, creating a new file.

        Args:
            file_name (str): The name of the file to be created.
            file_data: The data of the file to be uploaded.
            mimetype (str, optional): The MIME type of the file. Defaults to None.
            parent_id (str, optional): The ID of the parent directory under which the file will be placed. Defaults to None.

        Returns:
            dict: The API response that includes the ID of the newly created file.
        """
        file_metadata = {"name": file_name, "parents": [parent_id]}
        media = MediaFileUpload(file_data, mimetype=mimetype)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id", supportsAllDrives=True)
            .execute()
        )
        return file

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

            print("{0} ({1})".format(file_info["name"], file_info["id"]))
            request = self.service.files().get_media(fileId=file_info["id"])
            file_header = io.FileIO(file_path, "wb")
            downloader = MediaIoBaseDownload(file_header, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

    def download(self, parent_id, pattern, dest):
        target_video_files = self.find_files_by_MIME(parent_id=parent_id, pattern=pattern)
        tmp_video_folder = dest
        if not os.path.exists(tmp_video_folder):
            os.makedirs(tmp_video_folder)
        self.download_files(target_video_files, tmp_video_folder)
        print(f"{len(target_video_files)} video files download complete")

    class Operator:
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

    class MIMEType:
        """
        파일 타입에 따른 MIME명명 규칙입니다.
        """

        VIDEO = "video/mp4"
        IMAGE = "image/png"
        CSV = "text/csv"
        ICON = "image/x-icon"
        JSON = "application/json"
        PDF = "application/pdf"
        ZIP = "application/zip"
        TXT = "text/plain"
        DIR = "application/vnd.google-apps.folder"
