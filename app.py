import streamlit as st
from datetime import datetime

import config
from database import CampaniaDatabase
from models import CampaniaOrder
from audit import AuditLogger
from notifications import EmailNotifier, notify_new_request, notify_minimum_reached

from settings import SettingsManager, render_settings_panel


st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

db = CampaniaDatabase()
settings_manager = SettingsManager(db.sheet)
audit_logger = AuditLogger(db.sheet)
notifier = EmailNotifier(settings_manager)


def format_date(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
    except (ValueError, TypeError):
        return timestamp_str or "—"


def safe_index(options, value, default=0):
    try:
        return options.index(value)
    except ValueError:
        return default


def check_and_notify_minimum(db, notifier):
    """
    Re-checks the Paid pool against the minimum after any add/edit and
    fires an alert if it's met. No "already notified" tracking yet, so
    this can re-fire on later saves while the pool stays above minimum.
    """
    orders = db.get_all_orders()
    paid_orders = [o for o in orders if o.order_status == "Paid"]
    total = sum(o.campania_cost for o in paid_orders)

    if total >= config.DEFAULT_MINIMUM_ORDER:
        notify_minimum_reached(notifier, paid_orders, total)


@st.dialog("➕ New Request")
def new_request_dialog(db, notifier, audit_logger):

    customer_name = st.text_input("Customer Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    product = st.text_input("Product Requested")
    quantity = st.number_input("Quantity", min_value=1, value=1)
    notes = st.text_area("Notes")

    with st.expander("Advanced Fields"):
        street_address = st.text_input("Street Address")
        city = st.text_input("City")
        state = st.text_input("State")
        zip_code = st.text_input("Zip Code")
        campania_sku = st.text_input("Campania SKU")

        c1, c2 = st.columns(2)
        with c1:
            customer_price = st.number_input("Customer Price", min_value=0.0, step=1.0)
        with c2:
            campania_cost = st.number_input("Campania Cost", min_value=0.0, step=1.0)

        deposit_amount = st.number_input("Deposit Amount", min_value=0.0, step=1.0)

        col_d, col_i = st.columns(2)
        with col_d:
            delivery_required = st.toggle("Delivery")
            delivery_cost = st.number_input(
                "Delivery Cost", min_value=0.0, step=1.0
            ) if delivery_required else 0.0
        with col_i:
            install_required = st.toggle("Install")
            install_cost = st.number_input(
                "Install Cost", min_value=0.0, step=1.0
            ) if install_required else 0.0

        order_status = st.selectbox("Order Status", config.ORDER_STATUS_OPTIONS)
        payment_status = st.selectbox("Payment Status", config.PAYMENT_STATUS_OPTIONS)
        expected_arrival_date = st.text_input("Expected Arrival Date")

    if st.button("Create Request", type="primary", use_container_width=True):

        if not customer_name or not phone:
            st.warning("Customer Name and Phone are required.")
        else:
            new_order = CampaniaOrder.new(
                customer_name=customer_name,
                customer_phone=phone,
                product_requested=product,
                customer_email=email,
                notes=notes
            )

            new_order.quantity = quantity
            new_order.street_address = street_address
            new_order.city = city
            new_order.state = state
            new_order.zip_code = zip_code
            new_order.campania_sku = campania_sku
            new_order.customer_price = customer_price
            new_order.campania_cost = campania_cost
            new_order.deposit_amount = deposit_amount
            new_order.delivery_required = delivery_required
            new_order.delivery_cost = delivery_cost
            new_order.install_required = install_required
            new_order.install_cost = install_cost
            new_order.order_status = order_status
            new_order.payment_status = payment_status
            new_order.expected_arrival_date = expected_arrival_date

            new_id = db.add_order(new_order)

            audit_logger.log_change(
                request_id=new_id,
                customer_name=new_order.customer_name,
                field_name="Order Created",
                old_value="",
                new_value="Created"
            )

            notify_new_request(notifier, new_order)
            check_and_notify_minimum(db, notifier)

            st.success(f"Created Request {new_id}")
            st.rerun()


@st.dialog("Edit Order")
def edit_order_dialog(order, db, audit_logger, notifier):

    st.subheader(f"{order.customer_name} ({order.request_id})")
    rid = order.request_id

    c1, c2 = st.columns(2)
    with c1:
        customer_name = st.text_input("Customer Name", value=order.customer_name, key=f"name_{rid}")
        customer_phone = st.text_input("Phone", value=order.customer_phone, key=f"phone_{rid}")
        customer_email = st.text_input("Email", value=order.customer_email, key=f"email_{rid}")
        street_address = st.text_input("Street Address", value=order.street_address, key=f"addr_{rid}")
        city = st.text_input("City", value=order.city, key=f"city_{rid}")
    with c2:
        state = st.text_input("State", value=order.state, key=f"state_{rid}")
        zip_code = st.text_input("Zip Code", value=order.zip_code, key=f"zip_{rid}")
        product_requested = st.text_input("Product Requested", value=order.product_requested, key=f"product_{rid}")
        campania_sku = st.text_input("Campania SKU", value=order.campania_sku, key=f"sku_{rid}")
        quantity = st.number_input("Quantity", min_value=1, value=order.quantity, key=f"qty_{rid}")

    notes = st.text_area("Notes", value=order.notes, key=f"notes_{rid}")

    c3, c4, c5 = st.columns(3)
    with c3:
        customer_price = st.number_input(
            "Customer Price", min_value=0.0, value=order.customer_price, step=1.0, key=f"cprice_{rid}"
        )
    with c4:
        campania_cost = st.number_input(
            "Campania Cost", min_value=0.0, value=order.campania_cost, step=1.0, key=f"ccost_{rid}"
        )
    with c5:
        deposit_amount = st.number_input(
            "Deposit Amount", min_value=0.0, value=order.deposit_amount, step=1.0, key=f"deposit_{rid}"
        )

    col_d, col_i = st.columns(2)
    with col_d:
        delivery_required = st.toggle("Delivery", value=order.delivery_required, key=f"delreq_{rid}")
        if delivery_required:
            delivery_cost = st.number_input(
                "Delivery Cost", min_value=0.0, value=order.delivery_cost, step=1.0, key=f"delcost_{rid}"
            )
            delivery_status = st.selectbox(
                "Delivery Status",
                config.DELIVERY_STATUS_OPTIONS,
                index=safe_index(config.DELIVERY_STATUS_OPTIONS, order.delivery_status),
                key=f"delstatus_{rid}"
            )
        else:
            delivery_cost = 0.0
            delivery_status = "N/A"
            st.caption("Delivery Status: N/A")

    with col_i:
        install_required = st.toggle("Install", value=order.install_required, key=f"instreq_{rid}")
        if install_required:
            install_cost = st.number_input(
                "Install Cost", min_value=0.0, value=order.install_cost, step=1.0, key=f"instcost_{rid}"
            )
            install_status = st.selectbox(
                "Install Status",
                config.INSTALL_STATUS_OPTIONS,
                index=safe_index(config.INSTALL_STATUS_OPTIONS, order.install_status),
                key=f"inststatus_{rid}"
            )
        else:
            install_cost = 0.0
            install_status = "N/A"
            st.caption("Install Status: N/A")

    c6, c7 = st.columns(2)
    with c6:
        payment_status = st.selectbox(
            "Payment Status",
            config.PAYMENT_STATUS_OPTIONS,
            index=safe_index(config.PAYMENT_STATUS_OPTIONS, order.payment_status),
            key=f"paystatus_{rid}"
        )
    with c7:
        order_status = st.selectbox(
            "Order Status",
            config.ORDER_STATUS_OPTIONS,
            index=safe_index(config.ORDER_STATUS_OPTIONS, order.order_status),
            key=f"orderstatus_{rid}"
        )

    expected_arrival_date = st.text_input(
        "Expected Arrival Date", value=order.expected_arrival_date, key=f"eta_{rid}"
    )

    if st.button("💾 Save", type="primary", use_container_width=True):

        # Built directly from form values (not round-tripped through from_dict),
        # which is what was causing the old save-everything-blank bug.
        updated = CampaniaOrder(
            request_id=order.request_id,
            created_timestamp=order.created_timestamp,
            last_modified_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            product_requested=product_requested,
            campania_sku=campania_sku,
            quantity=quantity,
            notes=notes,
            customer_price=customer_price,
            campania_cost=campania_cost,
            deposit_amount=deposit_amount,
            delivery_required=delivery_required,
            delivery_cost=delivery_cost,
            delivery_status=delivery_status,
            payment_status=payment_status,
            order_status=order_status,
            expected_arrival_date=expected_arrival_date,
            install_required=install_required,
            install_status=install_status,
            install_cost=install_cost
        )

        audit_logger.log_order_changes(
            request_id=order.request_id,
            customer_name=updated.customer_name,
            old_dict=order.to_dict(),
            new_dict=updated.to_dict()
        )

        db.update_order(updated)
        check_and_notify_minimum(db, notifier)

        st.success("Saved")
        st.rerun()


def render_order_card(order, db, audit_logger, notifier):
    with st.container(border=True):
        st.markdown(f"**{order.customer_name}**")
        st.caption(f"Created {format_date(order.created_timestamp)}")

        st.write(f"SKU: {order.campania_sku or '—'}")

        c1, c2 = st.columns(2)
        with c1:
            st.write(f"Cost: ${order.campania_cost:,.2f}")
        with c2:
            st.write(f"Price: ${order.customer_price:,.2f}")

        color = config.STATUS_COLORS.get(order.order_status, "#6B7280")
        st.markdown(
            f'<span style="background-color:{color}; color:white; '
            f'padding:2px 10px; border-radius:6px; font-size:0.85em;">'
            f'{order.order_status}</span>',
            unsafe_allow_html=True
        )

        if st.button("Edit", key=f"edit_{order.request_id}", use_container_width=True):
            edit_order_dialog(order, db, audit_logger, notifier)


def render_order_grid(orders_list, db, audit_logger, notifier, empty_message):
    if not orders_list:
        st.caption(empty_message)
        return

    cols_per_row = 3
    for i in range(0, len(orders_list), cols_per_row):
        row_orders = orders_list[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, order in zip(cols, row_orders):
            with col:
                render_order_card(order, db, audit_logger, notifier)


st.title("📦 Campania Order Dashboard")

if st.button("➕ New Request", type="primary"):
    new_request_dialog(db, notifier, audit_logger)

orders = db.get_all_orders()

if not orders:
    st.info("No orders yet — add your first request above.")
else:

    st.sidebar.header("Filters")

    customer_filter = st.sidebar.text_input("Search Customer")
    product_filter = st.sidebar.text_input("Search Product")
    status_filter = st.sidebar.selectbox(
        "Order Status",
        ["All"] + config.ACTIVE_STATUSES
    )

    if customer_filter:
        orders = [o for o in orders if customer_filter.lower() in o.customer_name.lower()]

    if product_filter:
        orders = [o for o in orders if product_filter.lower() in o.product_requested.lower()]

    leads_orders = [o for o in orders if o.order_status in config.LEAD_STATUSES]
    active_orders = [o for o in orders if o.order_status in config.ACTIVE_STATUSES]

    # Computed before the status dropdown filters the displayed grid below,
    # so the metric always reflects the full Paid pool, not just what's shown.
    paid_orders = [o for o in active_orders if o.order_status == "Paid"]
    awaiting_total = sum(o.campania_cost for o in paid_orders)

    if status_filter != "All":
        active_orders = [o for o in active_orders if o.order_status == status_filter]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Awaiting Order Total", f"${awaiting_total:,.2f}")
        if awaiting_total >= config.DEFAULT_MINIMUM_ORDER:
            st.markdown(
                '<span style="color:#22C55E; font-weight:600;">Minimum Met</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span style="color:#EF4444; font-weight:600;">Below Minimum</span>',
                unsafe_allow_html=True
            )

    with col2:
        st.metric("Active Orders", len(active_orders))

    with col3:
        if active_orders:
            oldest = min(active_orders, key=lambda o: o.created_timestamp)
            st.metric("Oldest Request", oldest.customer_name)
            st.caption(oldest.product_requested)
        else:
            st.metric("Oldest Request", "—")

    st.divider()

    st.subheader("Active Orders")
    render_order_grid(active_orders, db, audit_logger, notifier, "No active orders.")

    st.divider()

    st.subheader("🧾 Sales Leads")
    render_order_grid(leads_orders, db, audit_logger, notifier, "No leads right now.")


st.divider()

col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    if st.button("⚙️ Settings", use_container_width=True):
        render_settings_panel(settings_manager)