import streamlit as st
from utils import order_summary

def show(user):
    st.title("NGO Dashboard")
    ngo_name = user[1]

    st.subheader("Available Requests")
    has_available_orders = False
    for order in st.session_state.orders:
        if order["status"] != "Pending":
            continue

        has_available_orders = True
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write(f"Donor: {order['donor_name']}")
        col2.write(f"Qty: {order['food_qty']}")
        col3.write(f"Expiry: {order['expiry']} hrs")
        if col4.button("Accept", key=f"accept-{order['id']}"):
            order["status"] = "Accepted"
            order["assigned_ngo"] = ngo_name
            st.rerun()

    if not has_available_orders:
        st.info("No pending food requests are available.")

    st.subheader("Accepted Orders")
    for order in st.session_state.orders:
        if order["assigned_ngo"] != ngo_name or order["status"] not in ("Accepted", "Assigned"):
            continue

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write(f"Order #{order['id']} from {order['donor_name']}")
        col2.write(f"Qty: {order['food_qty']}")
        col3.write(order["status"])
        if col4.button("Complete", key=f"complete-{order['id']}"):
            order["status"] = "Completed"
            st.rerun()

    st.dataframe(
        [
            order_summary(order)
            for order in st.session_state.orders
            if order["assigned_ngo"] == ngo_name
        ],
        use_container_width=True,
    )
