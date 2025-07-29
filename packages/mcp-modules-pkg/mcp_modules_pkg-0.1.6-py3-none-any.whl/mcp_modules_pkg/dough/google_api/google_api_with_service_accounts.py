# -*- coding: utf-8 -*-

import os
import pickle
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from dough.google_api.base import GoogleApiHelperBase


class GoogleApiWithServiceAccounts(GoogleApiHelperBase):
    def __init__(self, scopes: list, impersonate: str):
        super().__init__()
        SERVICE_ACCOUNT_FILE = (
            f'{os.environ["CREDENTIAL_ROOT"]}/masterapi-gcs_bitmango.json'
        )
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
        if impersonate:
            self.credentials = self.credentials.with_subject(impersonate)

    
class GoogleApiWithSheetServiceAccounts(GoogleApiHelperBase):
    def __init__(self, scopes: list):
        super().__init__()
        cred_dir = os.environ["CREDENTIAL_ROOT"]
        if os.path.exists(f"{cred_dir}/spreadsheet_token.pickle"):
            with open(f"{cred_dir}/spreadsheet_token.pickle", "rb") as token:
                self.credentials = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(f"{cred_dir}/spreadsheet_credentials.json", scopes)
                self.credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(cred_dir + "/spreadsheet_token.pickle", "wb") as token:
                pickle.dump(self.credentials, token)
