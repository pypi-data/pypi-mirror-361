from dough.management.base import Base

import requests


class ApplovinCampaignManagement(Base):
    def fetch_campaign(self, account: str, campaign_id: str) -> dict:
        endpoint = f"/applovin/campaign_management/v1/campaigns/{campaign_id}"
        params = {"account": account}
        try:
            url = f"{self.baseurl}{endpoint}"
            response = requests.get(url, params=params, timeout=500)
            campaign = response.json()
            return campaign
        except Exception as e:
            self.response_message("failed", f"Error fetching campaign: {e}")

    def fetch_campaign_targets(self, account, campaign):
        endpoint = f"/applovin/campaign_management/v1/campaign_targets/{campaign['campaign_id']}"
        params = {"account": account}
        try:
            url = f"{self.baseurl}{endpoint}"
            res = requests.get(url, params=params, timeout=500)
            return res.json()
        except Exception as err:
            self.response_message("fail", f"fetch campaign target api error : {err}")
