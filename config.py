"""
config.py

Application-wide configuration.

All environment-specific values should come from
Streamlit secrets.

No IDs or credentials should be hardcoded.
"""

import streamlit as st


# =====================================================
# GOOGLE SHEETS
# =====================================================

SHEET_ID = st.secrets["sheet_id"]

ORDERS_WORKSHEET = "Orders"
AUDIT_WORKSHEET = "Audit Log"
SETTINGS_WORKSHEET = "Settings"


# =====================================================
# APP SETTINGS
# =====================================================

APP_TITLE = "Campania Order Dashboard"

APP_ICON = "🏺"

DEFAULT_MINIMUM_ORDER = 2500.00


# =====================================================
# STATUS OPTIONS
# =====================================================

ORDER_STATUS_OPTIONS = [
    "Awaiting Quote",
    "Awaiting Customer Approval",
    "Awaiting Minimum Order",
    "Ready To Order",
    "Order Placed",
    "Arrived",
    "Picked Up",
    "Delivered",
    "Complete"
]


PAYMENT_STATUS_OPTIONS = [
    "No Quote Provided",
    "Estimate Provided",
    "Deposit Received",
    "Paid In Full"
]


DELIVERY_STATUS_OPTIONS = [
    "Not Needed",
    "Not Scheduled",
    "Scheduled",
    "Delivered"
]


# =====================================================
# COLORS
# =====================================================

STATUS_COLORS = {
    "Awaiting Quote": "#F97316",
    "Awaiting Customer Approval": "#FACC15",
    "Awaiting Minimum Order": "#EF4444",
    "Ready To Order": "#22C55E",
    "Order Placed": "#3B82F6",
    "Arrived": "#8B5CF6",
    "Picked Up": "#06B6D4",
    "Delivered": "#10B981",
    "Complete": "#6B7280",
}


# =====================================================
# COLUMN DEFINITIONS
# =====================================================

ORDER_COLUMNS = [
    "Request ID",
    "Created Timestamp",
    "Last Modified Timestamp",
    "Created By",
    "Last Modified By",

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

    "Expected Arrival Date"
]