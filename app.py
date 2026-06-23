import streamlit as st
import pandas as pd
from datetime import datetime

from database import CampaniaDatabase

SHEET_ID = st.secrets["sheet_id"]

db = CampaniaDatabase(SHEET_ID)

st.set_page_config(
    page_title="Campania Dashboard",
    layout="wide"
)

# ------------------------
# USER INITIALS
# ------------------------

if "initials" not in st.session_state:

    st.title("Campania Dashboard")

    initials = st.text_input(
        "Enter Your Initials"
    )

    if st.button("Continue"):

        st.session_state.initials = initials.upper()

        st.rerun()

    st.stop()

# ------------------------
# LOAD DATA
# ------------------------

df = db.get_orders()

if df.empty:

    df = pd.DataFrame(columns=[
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
    ])

# ------------------------
# KPI CARDS
# ------------------------

active_df = df[df["Order Status"] != "Complete"]

awaiting_df = df[
    df["Order Status"].isin(
        [
            "Awaiting Minimum Order",
            "Ready To Order"
        ]
    )
]

total_cost = pd.to_numeric(
    awaiting_df["Campania Cost"],
    errors="coerce"
).fillna(0).sum()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Current Awaiting Order",
        f"${total_cost:,.2f}"
    )

with col2:

    st.metric(
        "Active Requests",
        len(active_df)
    )

with col3:

    awaiting_approval = len(
        df[
            df["Order Status"] ==
            "Awaiting Customer Approval"
        ]
    )

    st.metric(
        "Awaiting Approval",
        awaiting_approval
    )

st.divider()

# ------------------------
# NEW REQUEST
# ------------------------

with st.expander("➕ New Request"):

    with st.form("new_request"):

        customer_name = st.text_input(
            "Customer Name"
        )

        phone = st.text_input(
            "Phone"
        )

        email = st.text_input(
            "Email"
        )

        product = st.text_input(
            "Product Requested"
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1
        )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Create Request"
        )

        if submitted:

            now = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            new_row = {
                "Request ID":
                    db.generate_request_id(),

                "Created Timestamp":
                    now,

                "Last Modified Timestamp":
                    now,

                "Created By":
                    st.session_state.initials,

                "Last Modified By":
                    st.session_state.initials,

                "Customer Name":
                    customer_name,

                "Customer Phone":
                    phone,

                "Customer Email":
                    email,

                "Product Requested":
                    product,

                "Quantity":
                    quantity,

                "Notes":
                    notes,

                "Payment Status":
                    "No Quote Provided",

                "Order Status":
                    "Awaiting Quote",

                "Delivery Status":
                    "Not Needed"
            }

            df = pd.concat(
                [
                    df,
                    pd.DataFrame([new_row])
                ],
                ignore_index=True
            )

            db.save_dataframe(df)

            st.success(
                "Request Created"
            )

            st.rerun()

# ------------------------
# ACTIVE ORDERS
# ------------------------

show_completed = st.checkbox(
    "Show Completed Requests"
)

if not show_completed:

    display_df = df[
        df["Order Status"] != "Complete"
    ]

else:

    display_df = df

st.subheader("Orders")

edited_df = st.data_editor(
    display_df,
    use_container_width=True,
    num_rows="fixed"
)

if st.button("Save Changes"):

    edited_df["Last Modified Timestamp"] = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    edited_df["Last Modified By"] = (
        st.session_state.initials
    )

    db.save_dataframe(edited_df)

    st.success(
        "Changes Saved"
    )