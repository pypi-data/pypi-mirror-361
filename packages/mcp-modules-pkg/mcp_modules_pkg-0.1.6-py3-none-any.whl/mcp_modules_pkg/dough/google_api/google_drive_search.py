import os

from dough.google_api.google_api_with_service_accounts import \
    GoogleApiWithServiceAccounts

# 🔹 이미지 및 비디오 MIME 타입 리스트
IMAGE_VIDEO_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-ms-wmv",
}


class DriveSearch(GoogleApiWithServiceAccounts):
    """
    Class for handling Google Drive search operations.

    Attributes:
        SCOPES (list): List of scopes for Google Drive API.
        service (googleapiclient.discovery.Resource): Google Drive service object.

    Author:
        tskim.
    """

    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.appdata",
        "https://www.googleapis.com/auth/drive.photos.readonly",
    ]

    def __init__(self, impersonate=None):
        """
        Initializes the DriveSearch class.

        Args:
            impersonate (str, optional): The email address of the user to impersonate.
        """
        super().__init__(self.SCOPES, impersonate)
        self.service = super().get_service(api="drive", version="v3")

    def get_all_files_in_folder(self, folder_id, parent_path=""):
        """
        Recursively explores files and subfolders within a specified folder.

        Args:
            folder_id (str): The ID of the folder to explore.
            parent_path (str, optional): The parent path of the folder.

        Returns:
            list: A list of dictionaries containing information about files.
        """
        file_list = []
        page_token = None

        while True:
            query = f"'{folder_id}' in parents and trashed=false"
            results = (
                self.service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, parents, createdTime)",
                    pageToken=page_token,
                    corpora="allDrives",  # 공유 드라이브 포함
                    supportsAllDrives=True,  # 공유 드라이브 지원 활성화
                    includeItemsFromAllDrives=True,  # 공유 드라이브 항목 포함
                )
                .execute()
            )

            items = results.get("files", [])
            for item in items:
                file_id = item["id"]
                file_name = item["name"]
                mime_type = item["mimeType"]
                created_time = item.get("createdTime", "")
                file_path = os.path.join(parent_path, file_name)
                file_parents = item.get("parents", [])

                if mime_type == "application/vnd.google-apps.folder":  # 폴더라면 재귀 호출
                    file_list.extend(self.get_all_files_in_folder(file_id, file_path))
                elif mime_type in IMAGE_VIDEO_MIME_TYPES:  # 이미지 또는 비디오만 추가
                    file_url = (
                        f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                    )
                    folder_link = (
                        f"https://drive.google.com/drive/folders/{file_parents[0]}"
                        if file_parents
                        else "Unknown"
                    )
                    file_list.append(
                        {
                            "asset": file_name,
                            "path": folder_link,
                            "url": file_url,
                            "created_time": created_time,
                            "mime_type": mime_type,
                        }
                    )

            page_token = results.get("nextPageToken")  # 다음 페이지 토큰 갱신
            if not page_token:
                break  # 모든 페이지를 다 가져오면 종료

        return file_list
