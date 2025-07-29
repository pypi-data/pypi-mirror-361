from abc import ABC 
from googleapiclient.discovery import build

class GoogleApiHelperBase(ABC):
    def __init__(self):
        self.SCOPES = []

    @property
    def get_scopes(self):
        """
        get scopes
        """
        return self.SCOPES

    @get_scopes.setter
    def set_scopes(self, scopes: list):
        """
        set scopes
        """
        self.SCOPES = scopes

    def get_service(self, api: str, version: str):
        service = build(
            api, version, credentials=self.credentials, cache_discovery=False
        )
        return service
