"""
settings.py

Settings management for Campania Order Dashboard.

All settings are stored in the Google Sheets "Settings" tab.

This allows non-technical updates without code changes.
"""

import streamlit as st
import config


# =====================================================
# DEFAULT SETTINGS (fallback if sheet is empty)
# =====================================================

DEFAULT_SETTINGS = {
    "notification_enabled": "TRUE",
    "silence_notifications": "FALSE",
    "minimum_order_threshold": str(config.DEFAULT_MINIMUM_ORDER),
    "notification_emails": ""
}


# =====================================================
# SETTINGS MANAGER
# =====================================================

class SettingsManager:

    def __init__(self, sheet):

        """
        sheet = gspread spreadsheet object
        """

        self.sheet = sheet

        try:
            self.ws = self.sheet.worksheet(config.SETTINGS_WORKSHEET)
        except Exception:
            self.ws = self.sheet.add_worksheet(
                title=config.SETTINGS_WORKSHEET,
                rows=100,
                cols=10
            )
            self._initialize_sheet()


    # ---------------------------------------------
    # INITIAL SETUP
    # ---------------------------------------------

    def _initialize_sheet(self):
        """
        Create default settings structure.
        """

        self.ws.update("A1:B5", [
            ["setting", "value"],
            ["notification_enabled", "TRUE"],
            ["silence_notifications", "FALSE"],
            ["minimum_order_threshold", str(config.DEFAULT_MINIMUM_ORDER)],
            ["notification_emails", ""]
        ])


    # ---------------------------------------------
    # READ SETTINGS
    # ---------------------------------------------

    def get_all_settings(self) -> dict:
        """
        Return all settings as a dictionary.
        """

        records = self.ws.get_all_records()

        if not records:
            return DEFAULT_SETTINGS

        settings = {}

        for row in records:
            key = row.get("setting")
            value = row.get("value")
            settings[key] = value

        # fill missing defaults
        for k, v in DEFAULT_SETTINGS.items():
            if k not in settings:
                settings[k] = v

        return settings


    def get(self, key: str, default=None):
        """
        Get single setting value.
        """

        settings = self.get_all_settings()
        return settings.get(key, default)


    # ---------------------------------------------
    # WRITE SETTINGS
    # ---------------------------------------------

    def update_setting(self, key: str, value: str):
        """
        Update a single setting in sheet.
        """

        records = self.ws.get_all_records()

        for idx, row in enumerate(records, start=2):  # row 1 = header

            if row.get("setting") == key:
                self.ws.update_cell(idx, 2, value)
                return True

        # if not found, append new row
        self.ws.append_row([key, value])
        return True


    # ---------------------------------------------
    # EMAIL HELPERS
    # ---------------------------------------------

    def get_notification_emails(self) -> list:
        """
        Return list of emails from comma-separated string.
        """

        raw = self.get("notification_emails", "")

        if not raw:
            return []

        return [e.strip() for e in raw.split(",") if e.strip()]


    def notifications_enabled(self) -> bool:
        return self.get("notification_enabled", "TRUE") == "TRUE"


    def notifications_silenced(self) -> bool:
        return self.get("silence_notifications", "FALSE") == "TRUE"


    def get_minimum_order(self) -> float:
        try:
            return float(self.get("minimum_order_threshold"))
        except:
            return config.DEFAULT_MINIMUM_ORDER


# =====================================================
# STREAMLIT SETTINGS UI (GEAR PANEL)
# =====================================================

def render_settings_panel(settings_manager: SettingsManager):
    """
    Simple settings UI (to be called inside app.py sidebar or modal)
    """

    st.subheader("⚙️ Settings")

    settings = settings_manager.get_all_settings()

    # -----------------------------------------
    # NOTIFICATION TOGGLE
    # -----------------------------------------

    enabled = st.checkbox(
        "Enable Notifications",
        value=settings_manager.notifications_enabled()
    )

    if st.button("Save Notification Setting"):
        settings_manager.update_setting(
            "notification_enabled",
            "TRUE" if enabled else "FALSE"
        )
        st.success("Updated")

    st.divider()

    # -----------------------------------------
    # SILENCE TOGGLE
    # -----------------------------------------

    silence = st.checkbox(
        "Silence Notifications (Testing Mode)",
        value=settings_manager.notifications_silenced()
    )

    if st.button("Save Silence Setting"):
        settings_manager.update_setting(
            "silence_notifications",
            "TRUE" if silence else "FALSE"
        )
        st.success("Updated")

    st.divider()

    # -----------------------------------------
    # MINIMUM ORDER
    # -----------------------------------------

    min_order = st.number_input(
        "Minimum Order Threshold",
        value=settings_manager.get_minimum_order(),
        step=100.0
    )

    if st.button("Save Minimum Order"):
        settings_manager.update_setting(
            "minimum_order_threshold",
            str(min_order)
        )
        st.success("Updated")

    st.divider()

    # -----------------------------------------
    # EMAIL LIST
    # -----------------------------------------

    emails = st.text_area(
        "Notification Emails (comma separated)",
        value=",".join(settings_manager.get_notification_emails())
    )

    if st.button("Save Emails"):
        settings_manager.update_setting(
            "notification_emails",
            emails
        )
        st.success("Updated")