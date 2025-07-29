import json
import os

from dough.db_connector.mysql import Mysql
from dough.management.base import Base


class AdwordsBase(Base):
    """Base class for Adwords management."""

    def get_credential_file(self, account, endpoint):
        """Get credentials from a JSON file based on the account and endpoint.

        Args:
            account (str): The account name.
            endpoint (str): The endpoint name.

        Returns:
            dict: The credentials for the specified account and endpoint.
        """
        path = os.environ["CREDENTIAL_ROOT"]
        path = path + "/adwords.json"
        with open(path, encoding="utf-8") as json_file:
            credentialFile = json.load(json_file)
        credential = ""
        for i in credentialFile:
            if i["account"] == account and i["endpoint"] == endpoint:
                credential = i
                break
        return credential

    def makeCreds(self, cred_type, cre):
        """Create credentials based on the credential type and data.

        Args:
            cred_type (str): The type of credential.
            cre (dict): The credential data.

        Returns:
            dict: The created credentials.
        """
        creds = {}
        for i in cre:
            if i in ("account", "endpoint"):
                continue
            if i == "id":
                creds[cred_type] = cre[i]
            else:
                creds[i] = cre[i]
        return creds

    def get_credential_by_account(self, account, endpoint):
        """Get credentials by account and endpoint.

        Args:
            account (str): The account name.
            endpoint (str): The endpoint name.

        Returns:
            tuple: The Adwords credentials, Googleads credentials, and manager IDs.
        """
        cre = self.get_credential_file(account, endpoint)
        adwords_creds = self.makeCreds("client_customer_id", cre)
        googleads_creds = self.makeCreds("login_customer_id", cre)
        googleads_creds["use_proto_plus"] = "True"
        manager_ids = cre["id"]
        return adwords_creds, googleads_creds, manager_ids

    def retrieve_customer_ids_by_repoid(self, repoid):
        """Retrieve customer IDs by repository ID.

        Args:
            repoid (str): The repository ID.

        Returns:
            str: The Adwords ID.
        """
        ms = Mysql("idb_marketing_report")
        query = f"""
        SELECT 
            adwords_id
        FROM
            ua_manager_clone
        WHERE
            repoid = "{repoid}" 
        """
        df = ms.query(query)
        return df.iloc[0]["adwords_id"]

    def get_customer_ids(self, client):
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        customer_ids = accessible_customers.resource_names
        customer_ids = [x.split("/")[1] for x in customer_ids]
        return customer_ids


class AdwordsCreativeManagement(AdwordsBase):
    """Class for managing Adwords creatives."""

    ...


class AdwordsCampaignManagement(AdwordsBase):
    """Class for managing Adwords campaigns.

    Attributes:
        None

    Author:
        tskim.
    """

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
