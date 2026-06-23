import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class CampaniaDatabase:

    def __init__(self, sheet_id):
        creds = Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": "project",
                "private_key_id": "key",
                "private_key": st.secrets["gcp_service_account"]["private_key"],
                "client_email": st.secrets["gcp_service_account"]["client_email"],
                "client_id": st.secrets["gcp_service_account"]["client_id"],
                "token_uri": "https://oauth2.googleapis.com/token"
            },
            scopes=SCOPES
        )

        gc = gspread.authorize(creds)

        self.sheet = gc.open_by_key(sheet_id)
        self.orders = self.sheet.worksheet("Orders")

    def get_orders(self):

        data = self.orders.get_all_records()

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)

    def save_dataframe(self, df):

        self.orders.clear()

        rows = [df.columns.tolist()] + df.fillna("").values.tolist()

        self.orders.update(rows)

    def generate_request_id(self):

        df = self.get_orders()

        if df.empty:
            return "CAM-0001"

        ids = df["Request ID"].dropna()

        if len(ids) == 0:
            return "CAM-0001"

        nums = [int(x.split("-")[1]) for x in ids]

        return f"CAM-{max(nums)+1:04d}"