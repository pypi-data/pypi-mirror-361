import json

import requests
from dough.db_connector.mysql import Mysql
from dough.management.base import Base


class MolocoCampaignManagement(Base):
    def parse_repoid(self, campaign_name: str) -> str:
        try:
            return campaign_name.split("-")[0].split(".")[-1]
        except IndexError:
            raise ValueError(f"Invalid campaign name format: {campaign_name}")

    def retrieve_ad_account(self) -> dict:
        db = Mysql("idb_marketing_report")
        sql = f"""
        SELECT moloco_id, moloco_account FROM ua_manager WHERE repoid = '{self.repoid}'
        """
        df = db.query(sql)
        ad_account = json.loads(df.to_json(orient="records"))
        return ad_account[0]

    def fetch_campaign(self, account: str, campaign_id: str) -> dict:
        endpoint = f"{self.baseurl}/moloco/v1/campaigns/{campaign_id}"
        params = {"account": account}
        try:
            response = requests.get(endpoint, params=params, timeout=500)
            campaign = response.json()["campaign"]
            return campaign
        except Exception as e:
            self.response_message("failed", f"Error fetching campaign: {e}")

    def fetch_ad_group(self, account: str, campaign_id: str, ad_group_id: str) -> dict:
        endpoint = f"{self.baseurl}/moloco/v1/ad-groups/{ad_group_id}"
        params = {"account": account, "campaign_id": campaign_id}
        try:
            response = requests.get(endpoint, params=params, timeout=500)
            ad_group = response.json()["ad_group"]
            return ad_group
        except Exception as e:
            self.response_message("failed", f"Error fetching ad group: {e}")

    def fetch_audience_target(
        self, account: str, audience_target_id: str, ad_account_id: str
    ) -> dict:
        endpoint = f"{self.baseurl}/moloco/v1/audience-targets/{audience_target_id}"
        params = {"account": account, "ad_account_id": ad_account_id}
        try:
            response = requests.get(endpoint, params=params, timeout=500)
            audience_target = response.json()["audience_target"]
            return audience_target
        except Exception as e:
            self.response_message("failed", f"Error fetching audience target: {e}")

    def retrieve_latest_campaign_configuration_by_campaign_id(self, campaign_id):
        """Retrieve latest campaign_configuration by campaign ID.

        Args:
            campaign_id (str): The campaign ID.

        Returns:
            pd.DataFrame: campaign configuration.
        """
        ms = Mysql("idb_marketing_report")
        query = f"""
        SELECT
            *
        FROM
            campaign_configuration
        WHERE
            campaign_id = "{campaign_id}"
        ORDER BY
            update_time DESC
        LIMIT 1
        """
        df = ms.query(query)
        return df

    def get_ad_groups(self, campaigns: "pd.DataFrame") -> list:
        ad_groups = []
        for _, row in campaigns.iterrows():
            self.repoid = campaigns["repoid"].iloc[0]
            ad_account = self.retrieve_ad_account()
            ad_group = self.fetch_ad_group(
                ad_account["moloco_account"], row["campaign_id"], row["adset_id"]
            )
            ad_group["account"] = ad_account["moloco_account"]
            ad_group["moloco_id"] = ad_account["moloco_id"]
            ad_groups.append(ad_group)
        return ad_groups

    def get_siteids(self, ad_groups: list) -> list:
        siteids = []
        for ad_group in ad_groups:
            audience_ids = ad_group["audience"].get("shared_audience_target_ids", [])
            for audience_id in audience_ids:
                audience_target = self.fetch_audience_target(
                    ad_group["account"], audience_id, ad_group["moloco_id"]
                )
                siteid = {
                    "account": ad_group["account"],
                    "application_id": ad_group["moloco_id"],
                    "campaign_id": ad_group["campaign_id"],
                    "adset_id": ad_group["id"],
                    "siteid": self.transform_blocked_ids(audience_target),
                    "status": "BLOCKED",
                    "audience_id": audience_id,
                }
                siteids.append(siteid)
        return siteids

    def transform_blocked_ids(self, audience_target: dict) -> str:
        targeting_condition = audience_target.get("targeting_condition", {})
        blocked_ids = targeting_condition.get("blocked_app_bundles", [])
        return blocked_ids