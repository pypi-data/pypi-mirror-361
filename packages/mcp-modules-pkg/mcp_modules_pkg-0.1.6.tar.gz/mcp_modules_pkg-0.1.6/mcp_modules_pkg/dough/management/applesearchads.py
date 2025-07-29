from dough.management.base import Base
from dough.db_connector.mysql import Mysql

import argparse
import requests

class AppleSearchAdsBase(Base):
    def __init__(self) -> None:
        self.baseurl = "https://masterapi.datawave.co.kr/api/v1/raw"

    def retrieve_orgid(self) -> str:
        db = Mysql("idb_marketing_report")
        sql = f"SELECT applesearchads_id as orgid FROM ua_manager_clone WHERE repoid = '{self.repoid}' LIMIT 1;"
        df = db.query(sql)
        return df.iloc[0]["orgid"]

    def get_header(self):
        orgid = self.retrieve_orgid()
        header = {"authorization": f"orgid={orgid}"}
        return header

class ApplesearchadsCampaignMangagement(AppleSearchAdsBase):

    def fetch_campaign(self, account: str, campaign_id: str) -> dict:
        endpoint = f"{self.baseurl}/applesearchads/api/v5/campaigns/{campaign_id}"
        params = {"account": account}
        try:
            response = requests.get(endpoint, params=params, headers=self.get_header(), timeout=500)
            campaign = response.json()
            return campaign["data"]
        except Exception as e:
            self.response_message("failed", f"Error fetching campaign: {e}")

    def fetch_adgroups(self, account: str, campaign_id: str):
        endpoint = f"{self.baseurl}/applesearchads/api/v5/campaigns/{campaign_id}/adgroups"
        params = {"account": account, "limit": 1000, "offset": 0}
        try:
            response = requests.get(endpoint, params=params, headers=self.get_header(), timeout=500)
            adgroups = response.json()
            return adgroups["data"]
        except Exception as e:
            self.response_message("failed", f"Error fetching ad groups: {e}")

class AppleSearchAdsKeywordManagement(AppleSearchAdsBase):

    def get_keywords_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        self.args = ap.parse_args()
    
    def get_keyword_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-keyword_id", "--keyword_id", required=True)
        ap.add_argument("-adset_id", "--adset_id", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        self.args = ap.parse_args()

    def delete_keyword_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-adset_id", "--adset_id", required=True)
        ap.add_argument("-keyword_id", "--keyword_id", required=True)
        self.args = ap.parse_args()

    def get_a_targeting_keyword_in_adgroup(self, campaign_id: str, adgroup_id: str, keyword_id: str):
        endpoint = f"{self.baseurl}/applesearchads/api/v5/campaigns/{campaign_id}/adgroups/{adgroup_id}/targetingkeywords/{keyword_id}"
        params = {"account": self.args.account}
        try:
            response = requests.get(endpoint, params=params, headers=self.get_header(), timeout=500)
            keyword = response.json()
            return keyword["data"]
        except Exception as e:
            self.response_message("failed", f"Error fetching keyword: {e}")

    def find_targeting_keywords_in_campaign_id(self, campaign_id):
        url = f"{self.baseurl}/applesearchads/api/v5/campaigns/{campaign_id}/adgroups/targetingkeywords/find"
        params = {"account": self.args.account}
        body = {
                   "pagination": {
                     "offset": 0,
                     "limit": 5000
                   },
                   "orderBy": [
                     {
                       "field": "id",
                       "sortOrder": "ASCENDING"
                     }
                   ],
                   "conditions": [
                     {
                       "field": "deleted",
                       "operator": "EQUALS",
                       "values": [
                         "false"
                       ]
                     }
                   ]
                }
        try:
            response = requests.post(url, params=params, json=body, headers=self.get_header(), timeout=500)
            keywords = response.json()
            return keywords["data"]
        except  Exception as e:
            self.response_message("failed", f"Error fetching keywords: {e}")