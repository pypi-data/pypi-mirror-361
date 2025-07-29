from io import StringIO
from dough.management.base import Base

import requests
import pandas as pd

class FacebookManagement(Base):
    
    def fetch_accounts(self) -> pd.DataFrame:
        url = "https://masterapi.datawave.co.kr/api/v1/management/facebook/get"
        params = {"account": self.args.account, "method": "accounts"}
        response = requests.get(url, params=params, timeout=300)
        accounts_df = pd.read_csv(StringIO(response.text))
        return accounts_df