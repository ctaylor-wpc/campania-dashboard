"""
settings.py

Settings management for Campania Order Dashboard.

Settings are stored in the Google Sheets "Settings" tab so they
can be changed without a code deploy. Minimum order threshold is
intentionally NOT here - it's hardcoded in config.py.
"""

import streamlit as st
import config


DEFAULT_SETTINGS = {
    "silence_notifications": "FALSE",
    "notification_emails": ""
}


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

    def _initialize_sheet(self):
        self.ws.update("A1:B3", [
            ["setting", "value"],
            ["silence_notifications", "FALSE"],
            ["notification_emails", ""]
        ])

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

        for k, v in DEFAULT_SETTINGS.items():
            if k not in settings:
                settings[k] = v

        return settings

    def get(self, key: str, default=None):
        settings = self.get_all_settings()
        return settings.get(key, default)

    def update_setting(self, key: str, value: str):
        records = self.ws.get_all_records()

        for idx, row in enumerate(records, start=2):  # row 1 = header

            if row.get("setting") == key:
                self.ws.update_cell(idx, 2, value)
                return True

        self.ws.append_row([key, value])
        return True

    def get_notification_emails(self) -> list:
        raw = self.get("notification_emails", "")

        if not raw:
            return []

        return [e.strip() for e in raw.split(",") if e.strip()]

    def notifications_silenced(self) -> bool:
        return self.get("silence_notifications", "FALSE") == "TRUE"


@st.dialog("⚙️ Settings")
def render_settings_panel(settings_manager: SettingsManager):
    """
    Settings modal - notifications are on by default, this just
    lets Chris silence them or update the recipient list.
    """

    silence = st.checkbox(
        "Silence Notifications",
        value=settings_manager.notifications_silenced(),
        help="Notifications are enabled by default. Check this to pause them."
    )

    emails = st.text_area(
        "Notification Emails (comma separated)",
        value=",".join(settings_manager.get_notification_emails())
    )

    if st.button("Save Settings", type="primary", use_container_width=True):
        settings_manager.update_setting(
            "silence_notifications",
            "TRUE" if silence else "FALSE"
        )
        settings_manager.update_setting("notification_emails", emails)
        st.success("Updated")
        st.rerun()