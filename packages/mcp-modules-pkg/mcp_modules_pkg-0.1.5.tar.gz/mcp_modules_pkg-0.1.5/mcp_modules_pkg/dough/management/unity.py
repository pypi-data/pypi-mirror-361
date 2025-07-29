import json

import requests

from dough.db_connector.mysql import Mysql
from dough.management.base import Base


class UnityCampaignManagement(Base):
    pid = "unity"

    def get_apps(self, account, organization_id):
        params = {'account': account}
        url = f'{self.baseurl}/{self.pid}/advertise/v1/organizations/{organization_id}/apps'
        response = requests.get(url=url, params=params, timeout=300)
        parsed_response = json.loads(response.text)
        return parsed_response

    def get_campaign_set_id_by_appid(self, account, organization_id, appid, campaign_name):
        apps_in_unity = self.get_apps(account, organization_id)
        apps_in_unity = apps_in_unity["results"]
        sql = f"""
            SELECT appid, application_id
            FROM marketing_report.campaign_configuration
            WHERE appid = "{appid}"
            AND campaign_name = "{campaign_name}"
            AND date = (SELECT max(date) FROM marketing_report.campaign_configuration WHERE campaign_name = '{campaign_name}')
            AND pid = 'unity'
            LIMIT 1
        """
        ms = Mysql("idb_marketing_report")
        df = ms.query(sql)
        campaign_set_id = df["application_id"].values[0]
        return campaign_set_id

    def fetch_campaign(self, account, organization_id, campaign_set_id, campaign_id):
        params = {'account': account}
        url = (f'{self.baseurl}/{self.pid}/advertise/v1/organizations/'
               f'{organization_id}/apps/{campaign_set_id}/campaigns/{campaign_id}')
        response = requests.get(url=url, params=params, timeout=300)
        campaign = json.loads(response.text)
        campaign["campaign_set_id"] = campaign_set_id
        return campaign

    def fetch_campaign_targeting(self, campaign_id: str, application_id: str):
        try:
            base_url = "https://masterapi.datawave.co.kr/api/raw/unity/advertise/v1"
            url = (
                f"{base_url}/organizations/{self.organization_id}"
                f"/apps/{application_id}/campaigns/{campaign_id}"
                f"/targeting?account={self.account}"
            )
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching campaign targeting: {e}")

    def get_campaign_set_id_and_bid_strategy(self, campaign_id):
        sql = f"""SELECT bid_strategy, application_id
                FROM campaign_configuration
                WHERE campaign_id = '{campaign_id}' AND bid_strategy IS NOT NULL
                LIMIT 1;"""
        ms = Mysql("idb_marketing_report")
        df = ms.query(sql)
        bid_strategy = df.iloc[0]["bid_strategy"]
        campaign_set_id = df.iloc[0]["application_id"]
        return bid_strategy, campaign_set_id
