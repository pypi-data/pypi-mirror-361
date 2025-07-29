from __future__ import annotations

import argparse
import json
import sys


class Base:
    baseurl = "https://masterapi.datawave.co.kr/api/raw"

    # Campaign Mangement Parse Args
    def get_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        self.args = ap.parse_args()

    def off_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-geo", "--geo", required=False)
        self.args = ap.parse_args()

    def bidding_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-geo", "--geo", required=True)
        ap.add_argument("-bid", "--bid", required=True)
        self.args = ap.parse_args()

    def budget_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-geo", "--geo", required=True)
        ap.add_argument("-budget", "--budget", required=True)
        self.args = ap.parse_args()

    # Creative Management Parse Args
    def get_creative_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-adset_id", "--adset_id", required=False, default=None)
        ap.add_argument("-ad_id", "--ad_id", required=False, default=None)
        self.args = ap.parse_args()

    def get_creatives_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        self.args = ap.parse_args()

    def adset_off_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-adset_id", "--adset_id", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        self.args = ap.parse_args()

    def ad_off_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-adset_id", "--adset_id", required=True)
        ap.add_argument("-ad_id", "--ad_id", required=True)
        self.args = ap.parse_args()

    # Siteid Management Parse Args
    def get_siteid_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-siteid", "--siteid", required=True)
        self.args = ap.parse_args()

    def off_siteid_method_parse_args(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-account", "--account", required=True)
        ap.add_argument("-campaign_id", "--campaign_id", required=True)
        ap.add_argument("-campaign_name", "--campaign_name", required=True)
        ap.add_argument("-siteid", "--siteid", required=True)
        self.args = ap.parse_args()


    def join_find_campaign(self, campaigns: list[dict], campaign_name_key: str) -> dict:
        for campaign in campaigns:
            if campaign[campaign_name_key] == self.args.campaign_name:
                return campaign
        self.response_message("fail", f"campaign not found. : {self.args.campaign_name}")
        return None

    def response_message(self, result, reason=""):
        message = {"result": result, "reason": reason}
        print(json.dumps(message))
        sys.exit()
