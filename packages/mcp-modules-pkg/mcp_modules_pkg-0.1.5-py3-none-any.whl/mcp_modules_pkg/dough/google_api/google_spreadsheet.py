# -*- coding: utf-8 -*-
import pandas as pd
from dough.google_api.google_api_with_service_accounts import \
    GoogleApiWithSheetServiceAccounts


class GoogleSpreadsheet(GoogleApiWithSheetServiceAccounts):
    """Handles interactions with Google Spreadsheets through Google Sheets API with service accounts.

    Inherits from GoogleApiWithSheetServiceAccounts which provides methods to authenticate and interact
    with Google APIs using service accounts.
    """
    
    SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ]

    def __init__(self):
        """Initializes the GoogleSpreadsheet class with necessary scopes."""
        super().__init__(self.SCOPES)
        self.service = self.get_service("sheets", "v4")

    def get_sheet_to_dataframe(self, spreadsheet_id: str, range: str) -> pd.DataFrame:
        """Retrieves a specific range of cells from a spreadsheet and returns it as a pandas DataFrame.

        Args:
            spreadsheet_id (str): The unique identifier for the spreadsheet.
            range (str): The A1 notation of the range to retrieve.

        Returns:
            pd.DataFrame: A DataFrame containing the values from the specified range.

        Raises:
            Exception: If no data could be retrieved from the specified range.
        """
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range).execute()
        values = result.get("values", [])
        if not values:
            raise Exception("No Data.")
        df = pd.DataFrame(values)
        df.columns = df.iloc[0]
        df = df[1:]
        return df

    def get_sheet_tab_names(self, spreadsheet_id: str) -> list:
        """Lists all the tab names in a given spreadsheet.

        Args:
            spreadsheet_id (str): The unique identifier for the spreadsheet.

        Returns:
            list: A list of tab names in the spreadsheet.
        """
        sheet = self.service.spreadsheets()
        gsheet = sheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = gsheet.get("sheets", {})
        tab_names = []
        for sheet in sheets:
            tab_name = sheet.get("properties").get("title")
            tab_names.append(tab_name)
        return tab_names
    
    def get_sheet_tab_id(self, spreadsheet_id: str, tab_name: str) -> str:
        """Finds and returns the ID of a specific tab in a spreadsheet by its name.

        Args:
            spreadsheet_id (str): The unique identifier for the spreadsheet.
            tab_name (str): The name of the tab to find.

        Returns:
            str: The ID of the tab.

        Raises:
            ValueError: If the tab with the specified name does not exist in the spreadsheet.
        """
        sheet = self.service.spreadsheets()
        gsheet = sheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = gsheet.get("sheets", {})
        for sheet in sheets:
            if sheet.get("properties").get("title") == tab_name:
                return sheet.get("properties").get("sheetId")
        raise ValueError(f"스프레드시트 ID '{spreadsheet_id}'에 탭 이름 '{tab_name}'이(가) 없습니다.")


if __name__ == "__main__":
    api = GoogleSpreadsheet()
