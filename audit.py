"""
audit.py

Audit logging system for Campania Order Dashboard.

Purpose:
- Track every change made to an order
- Provide immutable history of edits
- Support management review and troubleshooting

Design:
- Append-only Google Sheet ("Audit Log")
- One row per field change
"""

import streamlit as st
from datetime import datetime

import config


# =====================================================
# AUDIT LOGGER
# =====================================================

class AuditLogger:

    def __init__(self, sheet):

        """
        sheet = gspread spreadsheet object (from database layer)
        """

        self.sheet = sheet
        self.ws = self.sheet.worksheet(config.AUDIT_WORKSHEET)


# =====================================================
# CORE LOGGING FUNCTION
# =====================================================

    def log_change(
        self,
        request_id: str,
        customer_name: str,
        field_name: str,
        old_value,
        new_value,
        user_initials: str
    ):
        """
        Append a single change event to the audit log.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            self.ws.append_row([
                timestamp,
                user_initials,
                request_id,
                customer_name,
                field_name,
                str(old_value),
                str(new_value)
            ])

        except Exception as e:
            # Fail silently so main app never breaks
            print(f"Audit log failed: {e}")


# =====================================================
# BULK DIFF LOGGER
# =====================================================

    def log_order_changes(
        self,
        request_id: str,
        customer_name: str,
        old_dict: dict,
        new_dict: dict,
        user_initials: str
    ):
        """
        Compare two order states and log only differences.
        """

        for key in new_dict.keys():

            old_value = old_dict.get(key)
            new_value = new_dict.get(key)

            if old_value != new_value:

                self.log_change(
                    request_id=request_id,
                    customer_name=customer_name,
                    field_name=key,
                    old_value=old_value,
                    new_value=new_value,
                    user_initials=user_initials
                )