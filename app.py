import streamlit as st
import pandas as pd
from datetime import datetime

import config
from database import CampaniaDatabase
from models import CampaniaOrder


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

db = CampaniaDatabase()


# =====================================================
# SESSION STATE (INITIALS)
# =====================================================

if "initials" not in st.session_state:

    st.title("Campania Order Dashboard")

    st.write("Enter your initials to begin")

    initials = st.text_input("Initials (e.g. EMC, CT, TC)")

    if st.button("Continue") and initials:
        st.session_state.initials = initials.upper()
        st.rerun()

    st.stop()


user = st.session_state.initials


# =====================================================
# LOAD DATA
# =====================================================

orders = db.get_all_orders()

df = pd.DataFrame([o.to_dict() for o in orders]) if orders else pd.DataFrame()


if df.empty:
    st.info("No orders found.")
    st.stop()


# =====================================================
# FILTER OUT COMPLETED
# =====================================================

show_completed = st.sidebar.checkbox("Show Completed Orders", value=False)

if not show_completed:
    df = df[df["order_status"] != "Complete"]


# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

customer_filter = st.sidebar.text_input("Search Customer")
product_filter = st.sidebar.text_input("Search Product")
status_filter = st.sidebar.selectbox(
    "Order Status",
    ["All"] + config.ORDER_STATUS_OPTIONS
)

if customer_filter:
    df = df[df["customer_name"].str.contains(customer_filter, case=False, na=False)]

if product_filter:
    df = df[df["product_requested"].str.contains(product_filter, case=False, na=False)]

if status_filter != "All":
    df = df[df["order_status"] == status_filter]


# =====================================================
# KPI ROW
# =====================================================

st.title("📦 Campania Order Dashboard")

col1, col2, col3 = st.columns(3)


# Total awaiting order value
awaiting = df[df["order_status"].isin([
    "Awaiting Minimum Order",
    "Ready To Order"
])]

total_cost = pd.to_numeric(awaiting["campania_cost"], errors="coerce").fillna(0).sum()

with col1:
    if total_cost >= config.DEFAULT_MINIMUM_ORDER:
        st.metric("Awaiting Order Total", f"${total_cost:,.2f}", delta="Ready")
    else:
        st.metric("Awaiting Order Total", f"${total_cost:,.2f}", delta="Below Minimum")


# Active orders
with col2:
    st.metric("Active Orders", len(df))


# Oldest request
with col3:
    df_sorted = df.sort_values("created_timestamp", ascending=True)
    oldest = df_sorted.iloc[0] if not df_sorted.empty else None

    if oldest is not None:
        st.metric(
            "Oldest Request",
            oldest["customer_name"],
            oldest["product_requested"]
        )


st.divider()


# =====================================================
# NEW REQUEST
# =====================================================

with st.expander("➕ New Request", expanded=False):

    with st.form("new_request_form"):

        c1, c2 = st.columns(2)

        with c1:
            customer_name = st.text_input("Customer Name", required=True)
            phone = st.text_input("Phone", required=True)
            email = st.text_input("Email")

        with c2:
            product = st.text_input("Product Requested")
            quantity = st.number_input("Quantity", min_value=1, value=1)

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Create Request")

        if submitted:

            new_order = CampaniaOrder.new(
                customer_name=customer_name,
                customer_phone=phone,
                created_by=user,
                product_requested=product,
                customer_email=email,
                notes=notes
            )

            new_order.quantity = quantity

            new_id = db.add_order(new_order)

            st.success(f"Created Request {new_id}")
            st.rerun()


# =====================================================
# EDITABLE TABLE
# =====================================================

st.subheader("Active Orders")

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    hide_index=True
)


# =====================================================
# SAVE CHANGES
# =====================================================

if st.button("💾 Save Changes"):

    for _, row in edited_df.iterrows():

        request_id = row["request_id"]

        existing = db.get_order_by_id(request_id)

        if not existing:
            continue

        updated = CampaniaOrder.from_dict(row.to_dict())

        updated.last_modified_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated.last_modified_by = user

        db.update_order(updated)

    st.success("Changes saved successfully")
    st.rerun()


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(f"Logged in as: {user}")