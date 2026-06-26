"""
config.py

Application-wide configuration.

All environment-specific values should come from
Streamlit secrets.

No IDs or credentials should be hardcoded.
"""

import streamlit as st


SHEET_ID = st.secrets["sheet_id"]

ORDERS_WORKSHEET = "Orders"
AUDIT_WORKSHEET = "Audit Log"
SETTINGS_WORKSHEET = "Settings"


APP_TITLE = "Campania Order Dashboard"
APP_ICON = "⛲"

# Hardcoded per Chris's request - no longer configurable in Settings
DEFAULT_MINIMUM_ORDER = 1500.00


ORDER_STATUS_OPTIONS = [
    "Lead",
    "Quoted",
    "Paid",
    "Ordered",
    "Received",
    "Complete"
]

# Statuses that belong in the Sales Leads section instead of Active Orders
LEAD_STATUSES = ["Lead", "Quoted"]

# Statuses shown in the Active Orders section. Complete is intentionally
# excluded - completed orders drop off the dashboard and only live in
# the spreadsheet. Change the status back to bring one onto the dashboard.
ACTIVE_STATUSES = ["Paid", "Ordered", "Received"]

PAYMENT_STATUS_OPTIONS = [
    "N/A",
    "Deposit Taken",
    "Invoiced",
    "Paid in Full"
]

DELIVERY_STATUS_OPTIONS = [
    "N/A",
    "In Queue",
    "Delivered"
]

INSTALL_STATUS_OPTIONS = [
    "N/A",
    "In Queue",
    "Installed"
]

STATUS_COLORS = {
    "Lead": "#F97316",
    "Quoted": "#FACC15",
    "Paid": "#3B82F6",
    "Ordered": "#8B5CF6",
    "Received": "#06B6D4",
    "Complete": "#6B7280",
}


ORDER_COLUMNS = [
    "Request ID",
    "Created Timestamp",
    "Last Modified Timestamp",

    "Customer Name",
    "Customer Phone",
    "Customer Email",

    "Street Address",
    "City",
    "State",
    "Zip Code",

    "Product Requested",
    "Campania SKU",
    "Quantity",
    "Notes",

    "Customer Price",
    "Campania Cost",
    "Deposit Amount",

    "Delivery Required",
    "Delivery Cost",
    "Delivery Status",

    "Payment Status",
    "Order Status",

    "Expected Arrival Date",

    "Install Required",
    "Install Status",

    # New - must exist as a new column at the END of the "Orders" sheet
    "Install Cost"
]