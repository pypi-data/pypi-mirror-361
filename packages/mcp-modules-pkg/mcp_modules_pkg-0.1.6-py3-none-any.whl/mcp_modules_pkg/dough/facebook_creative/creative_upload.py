"""
    페이스북에 소재를 자동업로드를 하기 위한 스크립트입니다.
"""
import os
import json
import time
from typing import Union
import pandas as pd
from dough.facebook_creative.fb_caller import ApiCaller
from dough.facebook_creative.upload_helper import UploadHelper

class AutoUploader:
    """자동업로드와 관련된 내용을 담고 있는 class입니다"""
    def __init__(self, target_date) -> None:
        self.apicaller = ApiCaller()
        self.helper = UploadHelper()
        self.target_date = target_date
        self.file_path = f"{os.environ['AIRFLOW_TMP']}/facebook/{self.target_date}"
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        #self.df_info = pd.read_csv(f"{self.file_path}/sample3.csv")
        #self.df_info = self.df_info.astype(str)

    def get_file_path(self):
        """file_path를 반환합니다."""
        return self.file_path

    def set_upload_info(self,active_adaccount, appids) -> Union[pd.DataFrame, None]:
        """ 업로드에 필요한 정보를 만들어 주는 함수

        Args:
            active_adaccount (_type_): facebook account 정보
            appids (_type_): appid list
        Note:
            * facebook name에 가끔 공백이 잘못 들어가있는 경우가 있어서 (휴먼에러) 공백 제거를 해준다.
            Name Processing
            sample name : com.bitmango.go.bunnypopbubble-facebook-ww-iap_99-bd

            repoid : com.bitmango.go.bunnypopbubble 이 형태에서 bunnypopbubble을 뽑아낸다.
            os : com.bitmango.go.bunnypopbubble 중 go 를 추출
            roimon db에서 가져온 appid에 com.bitmango.go.bunnypopbubble이 있는지 체크한다.

            ** name에 -split, playable
            campaign_name에 -split, sns, playable 이 들어간 캠페인
            adset은 자동업로드에서 제외된다.
            targeting에 instagram keyword가 있으면 Use_insta를 True로 설정해준다.
        """
        df_creative_info_file = self.helper.refresh_creative_spreadsheet()
        df_target_creative_info = self.helper.get_target_campaign()
        target_campaign_names = df_target_creative_info['campaign_name'].tolist()
        df_erase_string = self.helper.get_erase_string()
        adset_string = df_erase_string.loc[0, 'adset'] # 인덱스가 다르다면 인덱스 값을 변경하세요
        campaign_string = df_erase_string.loc[0, 'campaign']
        result = []
        for adaccount in active_adaccount:
            path = f"/{adaccount['id']}/campaigns"
            querystring = "account=bitmango"\
                "&fields=id,name,bid_strategy"\
                "&effective_status=[\"ACTIVE\"]"
            campaign_data = self.apicaller.graphapi_get(path, querystring)
            if campaign_data is not None:
                df_campaign_info = pd.DataFrame(campaign_data['data'])
            else:
                print("campaign_data is None")
                continue
            path = f"/{adaccount['id']}/adsets"
            querystring = "account=bitmango"\
                "&fields=id,name,targeting,bid_strategy,campaign_id"\
                "&effective_status=[\"ACTIVE\"]"
            adset_data = self.apicaller.graphapi_get(path, querystring)
            if adset_data is not None:
                df_adset_info = pd.DataFrame(adset_data["data"])
            else:
                print("adset_data is None")
                continue
            if not df_campaign_info.empty and not df_adset_info.empty:
                df_campaign_info = df_campaign_info.rename(
                    columns={
                        "id":"campaign_id",
                        "name":"campaign_name",
                        "bid_strategy":"campaign_bid_strategy"
                })
                df_merged = pd.merge(
                    df_adset_info,
                    df_campaign_info,
                    left_on="campaign_id",
                    right_on="campaign_id",
                    how="left"
                )
                df_merged["adaccount_id"] = adaccount["id"].split("_")[1]
                result.append(df_merged)
        df_concat = pd.concat(result)
        df_concat = df_concat[df_concat['campaign_name'].isin(target_campaign_names)]
        print(df_concat['campaign_name'].tolist())
        df_concat = df_concat[~df_concat["name"].str.contains(adset_string) &
            ~df_concat["campaign_name"].str.contains(campaign_string)]
        print(df_concat['campaign_name'].tolist())
        df_concat["name"] = df_concat["name"].str.replace(" ","")
        df_concat["repoid"] = df_concat["name"].apply(lambda x: x.split("-")[0].split(".")[-1])
        df_concat["os"] = df_concat["name"].apply(lambda x: x.split("-")[0].split(".")[-2])
        df_concat = df_concat[df_concat["name"].apply(lambda x: x.split("-")[0] in appids)]
        df_concat["targeting"] = df_concat["targeting"].astype(str)
        df_concat["use_insta"] = df_concat["targeting"].str.contains("instagram")
        df_info = pd.merge(
            df_concat,
            df_creative_info_file,
            left_on="repoid",
            right_on="appname",
            how="left"
        )
        df_info["url"] = df_info.apply(lambda row: row["url_ios"] if row["os"] == "ap"
                                        else row["url_android"] if row["os"] == "go"
                                        else row["url_amazon"] if row["os"] == "am"
                                        else None, axis=1)
        df_info = df_info[df_info.apply(
            self.helper.check_valid_creative_csv_content,
            axis=1
        )]
        df_info = df_info.astype(str)
        if df_info.empty:
            print("adset info is empty")
            return None

        return df_info

    @staticmethod
    def make_image_ads_info(elem):
        """ 이미지 업로드에 필요한 facebook 정보 세팅해주는 함수

        Args:
            elem (_type_): upload info에 들어있는 row 정보

        Returns:
            _type_: json
        """
        object_story_spec = {
            "page_id" : elem["page_id"],
            "link_data": {
                "call_to_action" : {
                    "type" : elem["action_type"],
                    "value" : {
                        "application": elem["application"]
                    }
                },
                "link" : elem["url"],
                "image_hash" : elem["image_hash"],
                "message" : elem["message"],
                "name" : elem["title"]
            }
        }
        if elem["use_insta"] == "True" :
            object_story_spec["instagram_actor_id"] = elem["instagram_actor_id"]

        payload = {
            "name": elem["no_ext_name"],
            "adset_id" : elem["id"],
            "status" : "ACTIVE",
            "creative" : {
                "name": elem["title"],
                "degrees_of_freedom_spec": {
                    "creative_features_spec": {
                        "standard_enhancements": {
                        "enroll_status": "OPT_OUT"
                        }
                    }
                },
                "object_story_spec" : object_story_spec
            }
        }
        return json.dumps(payload).encode('utf-8')

    @staticmethod
    def make_video_ads_info(elem):
        """ 비디오 업로드에 필요한 facebook 정보 세팅해주는 함수

        Args:
            elem (_type_): upload info에 들어있는 row 정보

        Returns:
            _type_: json
        """
        object_story_spec = {
            "page_id" : elem["page_id"],
            "video_data": {
                "call_to_action" : {
                    "type" : elem["action_type"],
                    "value" : {
                        "application": elem["application"],
                        "link" : elem["url"]
                    }
                },
                "video_id" : elem["video_id"],
                "image_url" : elem["thumbnail_url"],
                "message" : elem["message"],
                "title" : elem["title"]
            }
        }
        if elem["use_insta"] == "True" :
            object_story_spec["instagram_actor_id"] = elem["instagram_actor_id"]

        payload = {
            "name": elem["no_ext_name"],
            "adset_id" : elem["id"],
            "status" : "ACTIVE",
            "creative" : {
                "name": elem["title"],
                "degrees_of_freedom_spec": {
                    "creative_features_spec": {
                        "standard_enhancements": {
                        "enroll_status": "OPT_OUT"
                        }
                    }
                },
                "object_story_spec" : object_story_spec
            }
        }
        return json.dumps(payload).encode('utf-8')

    def make_upload_info_to_dataframe(self, df_info, _type) -> pd.DataFrame:
        """이미지/비디오 업로드 정보를 만들어준다.

        Args:
            df_info (_type_):  set_init_info task에서 만들어진 기본 정보
            type (_type_): image 또는  video 

        Returns:
            pd.DataFrame: _description_
        """
        tmp_folder = f"{self.file_path}/{_type}"
        if os.path.isdir(tmp_folder):
            files = []
            for _fn in os.listdir(tmp_folder):
                try:
                    split_name = _fn.split("-")[0]
                    file_type = _fn.split(".")[1]
                    no_ext_name = _fn.split(".")[0]
                    files.append((_fn, split_name, file_type, no_ext_name))
                except IndexError:
                    print(f"Invalid file name {_fn}. It should contain '-' and '.'")
            df_file_list = pd.DataFrame(files, columns=["file_name", "repoid", "type", "no_ext_name"])
            print(df_file_list)
        else:
            print(f"{tmp_folder} does not exist.")
        print(df_file_list['repoid'].tolist())
        print(df_info['repoid'].tolist())
        df_merged = pd.merge(df_file_list,
            df_info,
            left_on="repoid",
            right_on="repoid",
            how= "left"
        )
        print(df_merged)
        if _type == 'image':
            df_merged["image_hash"] = None
        else:
            df_merged["thumbnail_url"] = None
            df_merged["default_thumbnail"] = None
            df_merged["video_id"] = None

            img_rows = df_merged[(df_merged["type"] == "png") | (df_merged["type"] == "jpg")]

            for _, png_row in img_rows.iterrows():
                matching_row_index = df_merged[df_merged["no_ext_name"] == png_row["no_ext_name"]].index
                df_merged.loc[matching_row_index, "default_thumbnail"] = png_row["file_name"]
        df_merged = df_merged.astype(str)
        return df_merged

    def video_status_check(self, video_id, interval=15, max_retries=4) -> bool:
        """비디오 업로드가 완료되었는지 체크하는 함수

        Args:
            video_id (_type_): check가 필요한 video_id
            interval (int, optional): Defaults to 15.
            max_retries (int, optional): Defaults to 4.

        Note:
            파일을 한번 다 올려놓고 video_id만 가지고 있다가 업로드가 다 끝나고 나서
            체크하는 방식으로 변경하는게 좋을 듯 -- 2023-05-08
        Returns:
            bool: _description_
        """
        path = f"/{video_id}"
        querystring = "account=bitmango&fields=status"
        retries = 0
        while retries < max_retries:
            status = self.apicaller.graphapi_get(path, querystring)
            if status["status"]["video_status"] == "ready":
                return True
            retries += 1
            time.sleep(interval)
        print(f"Max retries reached. video id {video_id}")
        return False

    def pre_upload_image_to_facebook(self,df_upload_info) -> pd.DataFrame:
        """ 이미지 광고를 만들기 위해서 미리 업로드 하는 함수

        Args:
            df_upload_info (_type_): 업로드 대상

        Returns:
            pd.DataFrame: 업로드 후 image_hash값이 들어간 정보
        """
        access_token = self.apicaller.get_access_token()
        for index, elem in df_upload_info.iterrows():
            if elem["type"] == "mp4":
                continue

            url = f"https://graph.facebook.com/v20.0/act_{elem['adaccount_id']}/adimages"

            with open(f"{self.file_path}/image/{elem['file_name']}","rb") as file:
                file_data = {"filename": file}
                data = {"access_token": access_token}
                res_json = self.apicaller.fetch_data(url,
                    method="POST",
                    payload=data,
                    file=file_data
                )
                # 유니코드 이스케이프 시퀀스를 실제 문자로 변환
            if isinstance(res_json, str):
                decoded_res_json_str = bytes(res_json, "utf-8").decode("unicode_escape")
                decoded_res_json = json.loads(decoded_res_json_str)
            elif isinstance(res_json, dict):
                decoded_res_json = {k: bytes(v, "utf-8").decode("unicode_escape") if isinstance(v, str) else v for k, v in res_json.items()}
            else:
                # res_json의 타입에 따라 적절한 처리를 수행
                print("respons의 형태가 잘못된것 같습니다.")
                print(res_json)
                pass
            image_hash = decoded_res_json["images"][elem["file_name"]]["hash"]
            df_upload_info.at[index, "image_hash"] = image_hash
        return df_upload_info

    def pre_upload_thumbnail_to_facebook(self,df_upload_info) -> pd.DataFrame:
        """ 썸네일을 만들기 위해서 이미지파일을 올리는 함수

        Note:
            *** [ 필수 ] ***
            썸네일용 이미지를 먼저 올리고 비디오를 업로드 한다
            비디오에 쓰이는 썸네일의 URL 주소를 알아야 하기 때문에 썸네일용 이미지를 먼저 업로드하여
            URL 주소를 알아온다.
            해당 URL 주소는 광고를 제작할 때 사용이 된다.

            비디오와 동일한 이름의 이미지는 해당 비디오의 썸네일용 이미지이다.
            no_ext_name 컬럼이 동일하다면 defaul_thumnail 컬럼이 동일하게 들어가야해서
            thumbnail_url_dict는 이를 체크하기 위한 변수

        """
        thumbnail_url_dict = {}
        access_token = self.apicaller.get_access_token()
        for _, elem in df_upload_info.iterrows():
            if elem["default_thumbnail"] == "None":
                continue
            if elem["type"] == "mp4":
                continue
            if elem["default_thumbnail"] in thumbnail_url_dict: #똑같은 정보에 대해 중복 request 방지
                elem["thumbnail_url"] = thumbnail_url_dict[elem["default_thumbnail"]]
                continue

            url = f"https://graph.facebook.com/v20.0/act_{elem['adaccount_id']}/adimages"

            with open(f"{self.file_path}/video/{elem['default_thumbnail']}","rb") as file:
                file_data = {"filename": file}
                data = {"access_token": access_token}
                res_json = self.apicaller.fetch_data(url,
                    method="POST",
                    payload=data,
                    file=file_data
                )
            thumbnail_url = res_json["images"][elem["default_thumbnail"]]["url"]
            elem["thumbnail_url"] = thumbnail_url

            # 새로 계산된 thumbnail_url을 저장합니다.
            thumbnail_url_dict[elem["default_thumbnail"]] = thumbnail_url

        for key, value in thumbnail_url_dict.items(): #동일한 내용을 가진 비디오 정보에 썸네일 URL 링크 업데이트
            df_upload_info.loc[df_upload_info["default_thumbnail"] == key, "thumbnail_url"] = value
        return df_upload_info

    def check_image_exist_in_adimages(self, df_upload_info) -> Union[pd.DataFrame, None]:
        """ 이미지가 이미 존재 하는지 체크하는 함수
        """
        adaccount_list = set(df_upload_info["adaccount_id"].dropna().tolist())
        access_token = self.apicaller.get_access_token()
        filterd_df_list = []
        df_uploadable = None
        for adaccount in adaccount_list:
            if pd.isna(adaccount) or adaccount == 'nan':
                continue
            url = f"https://graph-video.facebook.com/v20.0/act_{adaccount}/adimages"\
                f"?access_token={access_token}&limit=50&fields=name,id,hash"
            print(url)
            exists = self.apicaller.fetch_data(url)
            print(exists)
            if exists is not None and exists["data"] is not None:
                exists = pd.DataFrame(exists["data"])
            else:
                print(f"adimage is empty :: {exists}")
                continue
            df_tmp = df_upload_info[df_upload_info["adaccount_id"] == adaccount]
            df_tmp = df_tmp[~df_tmp["file_name"].isin(exists["name"])] #이미 업로드 된 파일 제거
            if not df_tmp.empty:
                filterd_df_list.append(df_tmp)

        if filterd_df_list:
            df_uploadable = pd.concat(filterd_df_list)
        return df_uploadable

    def check_video_exist_in_advideo(self, df_upload_info) -> Union[pd.DataFrame, None]:
        """ 비디오가 이미 존재하는지 체크하는 함수
            넘어오는 dataframe의 모든 값은 string값
            adaccount가 nan이 아니라 'nan'을 체크하는것은 string이라서
        """
        adaccount_list = set(df_upload_info["adaccount_id"].dropna().tolist())
        access_token = self.apicaller.get_access_token()
        filterd_df_list = []
        df_uploadable = None
        for adaccount in adaccount_list:
            if adaccount == 'nan':
                continue
            url = f"https://graph-video.facebook.com/v20.0/act_{adaccount}/advideos"\
                f"?access_token={access_token}&limit=50&fields=title,id"
            print(url)
            exists = self.apicaller.fetch_data(url)
            print(exists)
            if exists is not None and exists["data"] is not None:
                exists = pd.DataFrame(exists["data"])
            else:
                print(f"advideo is empty :: {exists}")
                continue
            df_tmp = df_upload_info[df_upload_info["adaccount_id"] == adaccount]
            df_tmp = df_tmp[~df_tmp["type"].isin(["png","jpg"])] # 이미지 파일 drop
            df_tmp = df_tmp[~df_tmp["file_name"].isin(exists["title"])] #이미 업로드 된 파일 제거
            if not df_tmp.empty:
                filterd_df_list.append(df_tmp)

        if filterd_df_list:
            df_uploadable = pd.concat(filterd_df_list)
        return df_uploadable

    def pre_upload_video_to_facebook(self, df_upload_info):
        """ 비디오 소재 미리 업로드 하는 함수

        Note:
            광고를 만들기에 앞서
            https://business.facebook.com/asset_library/ad_accounts
            해당 저장소에 Video 소재를 올리기 위한 함수

            * video 광고를 upload하는 url은 facebook graph api가 아닌 graph-video api를 사용한다.
            따라서 masterapi를 사용하지 않고 masterapi raw에 auth라는
            endpoint에서 facebook api 사용에 필요한 access_token을 받아와서 사용한다.

            ** video 소재와 동일한 이름의 png 파일이 있다면 해당 파일을 upload 한 뒤 URL 을 받아와 thumbnail로 사용한다.
            그렇지 않은 소재의 경우 facebook 에서 정해주는 thumbnail 후보 중 첫번째꺼를 thumbnail로 사용한다.

            dataframe을 순회하면서 video file을 업로드한다.
            upload 요청을 하고 나서 video의 status를 확인해 status가 ready 상태일 때 thumbnail 정보를 받아와
            광고를 만들 때 쓸 수 있도록 저장해둔다.
        """
        access_token = self.apicaller.get_access_token()
        for idx, elem in df_upload_info.iterrows():
            if elem["type"].lower() in ["png","jpg"]:
                continue
            url = "https://graph-video.facebook.com/v20.0"\
                f"/act_{elem['adaccount_id']}/advideos?"\
                f"access_token={access_token}"
            print(url)
            with open(f"{self.file_path}/video/{elem['file_name']}", "rb") as file:
                file_data = {"source": file}
                data = {"name": elem["file_name"]}
                advideo_info = self.apicaller.fetch_data(url, "POST", payload=data, file=file_data)
            df_upload_info.at[idx, "video_id"] = advideo_info["id"]
            if elem["thumbnail_url"] != "None":
                continue
            if self.video_status_check(advideo_info["id"]):
                path = f"/{advideo_info['id']}/thumbnails"
                querystring = "account=bitmango"
                thumbnail_info = self.apicaller.graphapi_get(path, querystring)
                df_upload_info.at[idx, "thumbnail_url"] = thumbnail_info['data'][0]['uri']
        return df_upload_info

def main():
    """standalone test를 위한 main 함수
    """

if __name__ == "__main__":
    main()


