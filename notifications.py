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

    def _send_email(self, subject: str, body: str, recipients: list, body_type: str = "plain"):

        if not recipients:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, body_type))

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

    def send(self, subject: str, message: str, body_type: str = "plain"):

        if not self._can_send():
            return False

        recipients = self.settings.get_notification_emails()

        return self._send_email(subject, message, recipients, body_type)


def notify_new_request(notifier: EmailNotifier, order):
    """
    Fired right after a new request is saved. Body is plain HTML built
    from string concatenation (same idea as a Google Apps Script
    GmailApp.sendEmail htmlBody) so Chris can restyle it directly here -
    swap labels, reorder lines, add more <b> tags, etc.
    """

    subject = "ALERT—New Campania Request"

    body = (
        "Here's all the information you need.<br><br>"
        f"<b>Request ID:</b> {order.request_id}<br>"
        f"<b>Customer Name:</b> {order.customer_name}<br>"
        f"<b>Customer Phone:</b> {order.customer_phone}<br>"
        f"<b>Customer Email:</b> {order.customer_email}<br>"
        f"<b>Street Address:</b> {order.street_address}<br>"
        f"<b>City:</b> {order.city}<br>"
        f"<b>State:</b> {order.state}<br>"
        f"<b>Zip Code:</b> {order.zip_code}<br>"
        f"<b>Product Requested:</b> {order.product_requested}<br>"
        f"<b>Campania SKU:</b> {order.campania_sku}<br>"
        f"<b>Quantity:</b> {order.quantity}<br>"
        f"<b>Notes:</b> {order.notes}<br>"
        f"<b>Customer Price:</b> ${order.customer_price:,.2f}<br>"
        f"<b>Campania Cost:</b> ${order.campania_cost:,.2f}<br>"
        f"<b>Deposit Amount:</b> ${order.deposit_amount:,.2f}<br>"
        f"<b>Delivery Required:</b> {'Yes' if order.delivery_required else 'No'}<br>"
        f"<b>Delivery Cost:</b> ${order.delivery_cost:,.2f}<br>"
        f"<b>Delivery Status:</b> {order.delivery_status}<br>"
        f"<b>Install Required:</b> {'Yes' if order.install_required else 'No'}<br>"
        f"<b>Install Cost:</b> ${order.install_cost:,.2f}<br>"
        f"<b>Install Status:</b> {order.install_status}<br>"
        f"<b>Payment Status:</b> {order.payment_status}<br>"
        f"<b>Order Status:</b> {order.order_status}<br>"
        f"<b>Expected Arrival Date:</b> {order.expected_arrival_date}<br>"
    )

    return notifier.send(subject, body, body_type="html")


def notify_minimum_reached(notifier: EmailNotifier, paid_orders: list, total_cost: float):
    """
    Fired whenever the Paid-but-not-yet-ordered pool crosses the minimum.
    Lists every live order counting toward the total. No "already sent"
    tracking yet, so this can re-fire on later edits while the pool stays
    above minimum - flag if a one-time-per-crossing alert is wanted instead.
    """

    subject = "ALERT—Campania Minimum Met"

    lines = [f"Campania order minimum has been reached. Current total: ${total_cost:,.2f}<br><br>"]

    for o in paid_orders:
        lines.append(
            f"<b>Customer Name:</b> {o.customer_name} &nbsp;&nbsp; "
            f"<b>Campania SKU:</b> {o.campania_sku} &nbsp;&nbsp; "
            f"<b>Campania Cost:</b> ${o.campania_cost:,.2f}<br>"
        )

    body = "".join(lines)

    return notifier.send(subject, body, body_type="html")


def notify_order_status_change(
    notifier: EmailNotifier,
    request_id: str,
    customer_name: str,
    product: str,
    old_status: str,
    new_status: str,
    user_initials: str = ""
):

    subject = f"Campania Order Update: {new_status}"

    message = f"""
Campania Order Status Update

Request ID: {request_id}
Customer: {customer_name}
Product: {product}

Status Change:
{old_status} → {new_status}

Updated By: {user_initials or '—'}
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