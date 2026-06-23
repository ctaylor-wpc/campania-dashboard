"""
notifications.py

Email notification system for Campania Order Dashboard.

Responsibilities:
- Send email alerts
- Respect settings (silenced / recipients)
- Provide reusable notification triggers

Design:
- Stateless functions where possible
- Safe failure (never breaks app)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import streamlit as st

import config


class EmailNotifier:

    def __init__(self, settings_manager):
        """
        settings_manager = SettingsManager instance
        """

        self.settings = settings_manager

        self.smtp_host = st.secrets.get("smtp_host", "")
        self.smtp_port = int(st.secrets.get("smtp_port", 587))
        self.smtp_user = st.secrets.get("smtp_user", "")
        self.smtp_pass = st.secrets.get("smtp_pass", "")
        self.from_email = st.secrets.get("from_email", self.smtp_user)

    def _send_email(self, subject: str, body: str, recipients: list):

        if not recipients:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.sendmail(self.from_email, recipients, msg.as_string())
            server.quit()

            return True

        except Exception as e:
            print(f"Email failed: {e}")
            return False

    def _can_send(self) -> bool:
        # Notifications are on by default - silencing is the only opt-out
        if self.settings.notifications_silenced():
            return False

        if not self.settings.get_notification_emails():
            return False

        return True

    def send(self, subject: str, message: str):

        if not self._can_send():
            return False

        recipients = self.settings.get_notification_emails()

        return self._send_email(subject, message, recipients)


def notify_minimum_reached(notifier: EmailNotifier, total_cost: float):

    subject = "Campania Order Minimum Reached"

    message = f"""
Campania Order Dashboard Alert

Minimum order threshold has been reached.

Current Total (Cost Basis): ${total_cost:,.2f}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action: Ready to submit order.
"""

    return notifier.send(subject, message)


def notify_order_status_change(
    notifier: EmailNotifier,
    request_id: str,
    customer_name: str,
    product: str,
    old_status: str,
    new_status: str,
    user_initials: str
):

    subject = f"Campania Order Update: {new_status}"

    message = f"""
Campania Order Status Update

Request ID: {request_id}
Customer: {customer_name}
Product: {product}

Status Change:
{old_status} → {new_status}

Updated By: {user_initials}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Dashboard: Campania Order System
"""

    return notifier.send(subject, message)


def notify_order_completed(
    notifier: EmailNotifier,
    request_id: str,
    customer_name: str,
    product: str
):

    subject = "Campania Order Completed"

    message = f"""
Campania Order Completed

Request ID: {request_id}
Customer: {customer_name}
Product: {product}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return notifier.send(subject, message)