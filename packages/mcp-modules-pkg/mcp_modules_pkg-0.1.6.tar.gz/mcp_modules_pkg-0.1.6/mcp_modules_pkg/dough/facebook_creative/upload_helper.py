"""
    페이스북 creative upload에 필요한 함수의 모음입니다.
"""
from typing import NoReturn, List, Dict
import os
import shutil
import pandas as pd
import gdoc
from dough.google_api.google_drive_downloader import GoogleDriveDownloader
from dough.facebook_creative.fb_caller import ApiCaller

class UploadHelper:
    """Upload에 필요한 작업들에 대한 함수
    """
    def __init__(self) -> None:
        self.apicaller = ApiCaller()

    def get_roimon_appids(self):
        """ roimon에서 appid 정보 가져온다.
        """
        data = self.apicaller.fetch_data(
            "https://roimon.datawave.co.kr/api/v3/apps?fields=appid"
        )
        if data is not None:
            appids = self.extract_data_from_json(data, "appid")
        return appids

    @staticmethod
    def refresh_creative_spreadsheet():
        """ 구글 스프레드 시크 정보 가져온다
        """
        doc_id = "1txgYjZ_sa4dLZv2reDFajYW49cP9L8aA4WCdlBoCsKc"
        tab_name = "creative_data"
        try :
            df_spreadsheet = gdoc.get(doc_id, tab_name, 0)
        except (IOError, TypeError) as error:
            print(f"크리에이티브 정보를 불러오지 못했습니다.{error}")
        return df_spreadsheet
    
    @staticmethod
    def get_target_campaign():
        doc_id = "1nCAz47WbjHMrV_Zag8KenyLTE2KbW66KNecXevTW25U"
        tab_name = "FB 자동업로드"
        try :
            df_spreadsheet = gdoc.get(doc_id, tab_name, 5)
        except (IOError, TypeError) as error:
            print(f"크리에이티브 정보를 불러오지 못했습니다.{error}")
        return df_spreadsheet
    
    @staticmethod
    def get_erase_string():
        doc_id = "1nCAz47WbjHMrV_Zag8KenyLTE2KbW66KNecXevTW25U"
        tab_name = "FB 자동업로드"
        try :
            spreadsheet_id = doc_id
            range_name = f"{tab_name}!C2:D3"  # Sheet1은 원하는 시트 이름으로 변경해주세요
            gsheet = gdoc.get_google_sheet(spreadsheet_id, range_name)
            data_info, header = gdoc.getData(gsheet,0)
            df_spreadsheet = pd.DataFrame(data_info)
            df_spreadsheet = df_spreadsheet[header]
        except (IOError, TypeError) as error:
            print(f"크리에이티브 정보를 불러오지 못했습니다.{error}")
        return df_spreadsheet

    def get_active_adaccount(self) -> List[Dict]:
        """ adaccount 정보 알아오는 함수

        Note:
            adaccount중 zzPaused 가 적힌 adaccount는 제외한다.
            zzAuto는 소재를 올릴 수 있기 때문에 제외하지 않음
        Returns:
            List[Dict]:
        """
        data = self.apicaller.graphapi_get(
            "/me/adaccounts",
            "account=bitmango&fields=id,name&limit=5000"
        )
        if not data["data"]:
            print("No Data found.")
            return []
        values = [d for d in data["data"] if "zzPaused" not in d["name"] ]
        return values

    @staticmethod
    def move_non_video_file(target_folder_name) -> NoReturn:
        """ image와 video용 파일을 구분해주는 함수

            Note:
            google drive facebook 소재 폴더에는 png파일과 mp4 파일이 혼재 되어 있음
            현재는 video 광고만 자동으로 업로드 하고 있어서 비디오 소재와 짝을 이루는 thumbnail 이미지만 올라가고 있는데
            image 광고 소재도 동일한 폴더에 올려서 쓰고 싶다고 전달받음
            하나의 폴더 (video) 에 모두 다운로드를 받고 두번째 인자로 필터링을 해서 파일을 옮기는 방향으로 결정
        """
        file_path = f"{os.environ['AIRFLOW_TMP']}/facebook/{target_folder_name}"
        tmp_video_folder = f"{file_path}/video"
        tmp_image_folder = f"{file_path}/image"
        os.makedirs(tmp_image_folder)
        video_files = os.listdir(tmp_video_folder)
        df_file_list = pd.DataFrame(video_files, columns=["file_name"])
        df_file_list["type"] = df_file_list["file_name"].apply(lambda x: x.split("-")[1])
        df_file_list = df_file_list[df_file_list["type"] != "video"]
        for _, elem in df_file_list.iterrows():
            shutil.move(f"{tmp_video_folder}/{elem['file_name']}",
                        f"{tmp_image_folder}/{elem['file_name']}")

    def copy_creative_file(self, target_folder_name) -> NoReturn:
        """ 소재를 다운 받는 함수

        Args:
            target_folder_name (_type_): 구글 드라이브에서 다운로드 받을 폴더의 이름

            * 구글 드라이브의 폴더 구조가 변경되면 해당 함수가 동작 하지 않을 수 있음
            구글 드라이브에 올라간 Creative 소재 파일을 업로드에 쓰기 위하여 로컬에 다운받을 때 사용하는 함수
            script의 같은 위치에 files라는 임시 공간에 입력받은 target_folder_name으로 폴더를 만들고 video, image 별로
            파일을 저장한다.
            업로드가 끝나고 나면 아래 empty_directory 를 호출하여 받은 파일들을 삭제 시킨다.
        Returns:
            NoReturn: _description_
        """
        drive_id = "1Tn9w9YTXDGbVwivQ5OLJj6XXiogn9t6T"
        downloader = GoogleDriveDownloader(None)
        file_path = f"{os.environ['AIRFLOW_TMP']}/facebook/{target_folder_name}"
        print(downloader)
        target_folder  = downloader.find_directories_by_name(
                pattern=f"name='{target_folder_name}'" ,parent_id=drive_id)
        print(target_folder)
        try :
            target_folder  = downloader.find_directories_by_name(
                pattern=f"name='{target_folder_name}'" ,parent_id=drive_id)
            #folder 구조가 바뀌어서 아래 facebook 폴더가 따로 생김
            target_facebook_folder  = downloader.find_directories_by_name(
                pattern="name='facebook'" ,parent_id=target_folder[0]["id"])
            downloader.download(parent_id=target_facebook_folder[0]["id"],
                                pattern=f"mimeType='{GoogleDriveDownloader.MIMEType.VIDEO}'",
                                dest= f"{file_path}/video")
            downloader.download(parent_id=target_facebook_folder[0]["id"],
                                pattern="mimeType='image/png'",
                                dest= f"{file_path}/video")
            downloader.download(parent_id=target_facebook_folder[0]["id"],
                                pattern="mimeType='image/jpeg'",
                                dest= f"{file_path}/video")
            self.move_non_video_file(target_folder_name)
        except IndexError as error : # 폴더가 없는 경우 Index 에러가 뜬다.
            print(f"target_folder_name :: {target_folder_name} :: {error} ")

    @staticmethod
    def empty_directory(dir_path) -> NoReturn:
        """ 타겟 디렉토리를 지우는 함수

        Args:
            dir_path (_type_): 삭제를 원하는 폴더의 PATH ./files/ 의 하위경로를 입력해줘야한다.

        """
        try:
            shutil.rmtree(dir_path)
            print(f"Directory '{dir_path}' and its contents have been deleted.")
        except FileNotFoundError:
            print(f"Directory '{dir_path}' not found.")
        except OSError as error:
            print(f"Error while deleting directory '{dir_path}': {error}")

    @staticmethod
    def check_valid_creative_csv_content(row):
        """ 조건 체크용 함수

        Note:
            conditions 안에 내용을 모두 통과해야한다.

            1. 메세지가 비어있으면 안된다.
            2. 타이틀이 비어있으면 안된다.
            3. 액션 타입이 비어있으면 안된다.
            4. 어플리케이션이 비어 있으면 안된다.
            5. URL이 비어있으면 안된다.
        """
        conditions = [
            row["message"] != '' and not pd.isna(row["message"]),
            row["title"] != '' and not pd.isna(row["title"]),
            row["action_type"] != '' and not pd.isna(row["action_type"]),
            row["application"] != '' and not pd.isna(row["application"]),
            row["url"] != '' and not pd.isna(row["url"])
        ]
        return all(conditions)

    @staticmethod
    def extract_data_from_json(data, key) -> list:
        """json데이터와 Key를 이용해서 데이터를 list로 추출한다 중복은 제거하고
        """
        col_data = [d[key] for d in data]
        ret = list(set(col_data))
        return ret
