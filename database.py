"""
database.py

Google Sheets interface layer for Campania Order Dashboard.

Key design principles:
- NEVER overwrite the full sheet
- Always update by Request ID
- Convert rows <-> CampaniaOrder model
- Safe for multi-user Streamlit usage
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import List, Optional

import config
from models import CampaniaOrder


# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

class CampaniaDatabase:

    def __init__(self):

        self.client = self._connect()
        self.sheet = self.client.open_by_key(config.SHEET_ID)

        self.orders_ws = self.sheet.worksheet(config.ORDERS_WORKSHEET)

    def _connect(self):
        """
        Authenticate using Streamlit secrets.
        """

        creds_info = st.secrets["gcp_service_account"]

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_info(
            creds_info,
            scopes=scopes
        )

        return gspread.authorize(creds)


# =====================================================
# READ OPERATIONS
# =====================================================

    def get_all_orders(self) -> List[CampaniaOrder]:
        """
        Fetch all orders from Google Sheets.
        """

        records = self.orders_ws.get_all_records()

        orders = []

        for r in records:
            try:
                orders.append(CampaniaOrder.from_dict(r))
            except Exception:
                continue

        return orders


    def get_orders_df(self) -> pd.DataFrame:
        """
        Return DataFrame for Streamlit display.
        """

        data = self.orders_ws.get_all_records()

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)


    def get_order_by_id(self, request_id: str) -> Optional[CampaniaOrder]:
        """
        Find a single order.
        """

        orders = self.get_all_orders()

        for o in orders:
            if o.request_id == request_id:
                return o

        return None


# =====================================================
# WRITE OPERATIONS
# =====================================================

    def add_order(self, order: CampaniaOrder) -> str:
        """
        Append a new order to the sheet.
        """

        last_id = self._get_last_request_id()
        order.request_id = CampaniaOrder.request_id or self._next_id(last_id)

        self.orders_ws.append_row(list(order.to_dict().values()))

        return order.request_id


    def update_order(self, updated_order: CampaniaOrder):
        """
        Update an existing order by Request ID.
        """

        cell = self.orders_ws.find(updated_order.request_id)

        if not cell:
            return False

        row_index = cell.row

        values = list(updated_order.to_dict().values())

        self.orders_ws.update(f"A{row_index}", [values])

        return True


    def update_field(self, request_id: str, field: str, value):
        """
        Update a single field safely.
        """

        cell = self.orders_ws.find(request_id)

        if not cell:
            return False

        headers = self.orders_ws.row_values(1)

        col_index = headers.index(field) + 1

        self.orders_ws.update_cell(cell.row, col_index, value)

        return True


# =====================================================
# ID MANAGEMENT
# =====================================================

    def _get_last_request_id(self) -> Optional[str]:
        """
        Get last Request ID in sheet.
        """

        records = self.orders_ws.get_all_records()

        if not records:
            return None

        return records[-1].get("Request ID")


    def _next_id(self, last_id: Optional[str]) -> str:
        """
        Generate next sequential ID.
        """

        if not last_id:
            return "CAM-0001"

        try:
            num = int(last_id.split("-")[1])
            return f"CAM-{num + 1:04d}"
        except Exception:
            return "CAM-0001"


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

    def delete_order(self, request_id: str):
        """
        Optional soft delete (mark Complete instead recommended).
        """

        self.update_field(request_id, "Order Status", "Complete")
        return True


    def mark_complete(self, request_id: str):
        """
        Safely complete an order.
        """

        self.update_field(request_id, "Order Status", "Complete")
        return True