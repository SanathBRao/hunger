import streamlit as st
from utils import (
    MAX_DELIVERY_DISTANCE,
    delivery_feasibility,
    distance_label,
    order_summary,
    sync_order_logistics,
)

def show(user):
    st.title("NGO Dashboard")
    ngo_name = user[1]
    st.subheader("NGO Location")
    ngo_x = st.number_input("NGO Location X", key="ngo-location-x")
    ngo_y = st.number_input("NGO Location Y", key="ngo-location-y")
    ngo_location = (ngo_x, ngo_y)
    st.session_state.ngo_locations[ngo_name] = ngo_location

    st.subheader("Available Requests")
    has_available_orders = False
    for order in st.session_state.orders:
        if order["status"] != "Pending":
            continue

        sync_order_logistics(order, ngo_location)
        label, color = distance_label(order["distance"])
        feasibility = delivery_feasibility(order)
        can_accept = feasibility == "Feasible"
        has_available_orders = True
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        col1.write(f"Donor: {order['donor_name']}")
        col2.write(f"Qty: {order['food_qty']}")
        col3.write(f"Expiry: {order['expiry']} hrs")
        col4.markdown(f":{color}[{label}: {order['distance']:.2f} km]")
        if col5.button("Accept", key=f"accept-{order['id']}", disabled=not can_accept):
            order["status"] = "Accepted"
            order["assigned_ngo"] = ngo_name
            order["ngo_location"] = ngo_location
            order["delivery_status"] = "In Transit"
            st.rerun()
        if not can_accept:
            st.caption(f"Order #{order['id']} cannot be accepted: {feasibility}")

    if not has_available_orders:
        st.info("No pending food requests are available.")

    st.subheader("Logistics Actions")
    for order in st.session_state.orders:
        if order["assigned_ngo"] != ngo_name or order["status"] not in ("Accepted", "Assigned", "Completed"):
            continue

        sync_order_logistics(order, ngo_location)
        label, color = distance_label(order["distance"])
        feasibility = delivery_feasibility(order)
        can_confirm = order["status"] in ("Accepted", "Assigned") and feasibility == "Feasible"
        can_distribute = order["delivery_status"] == "Delivered"

        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        col1.write(f"Order #{order['id']} from {order['donor_name']}")
        col2.write(f"Qty: {order['food_qty']}")
        col3.markdown(f":{color}[{label}: {order['distance']:.2f} km]")
        col4.write(order["delivery_status"])
        if col5.button("Confirm Delivery", key=f"deliver-{order['id']}", disabled=not can_confirm):
            order["delivery_status"] = "Delivered"
            order["status"] = "Completed"
            st.rerun()
        if not can_confirm and order["delivery_status"] != "Delivered":
            st.caption(
                f"Delivery blocked for order #{order['id']}: {feasibility}. "
                f"Limit is {MAX_DELIVERY_DISTANCE} km."
            )

        reason = st.selectbox(
            "Cancellation reason",
            ["Too far", "Expired", "Capacity issue"],
            key=f"cancel-reason-{order['id']}",
        )
        cancel_col, distribute_col = st.columns(2)
        if cancel_col.button("Cancel", key=f"cancel-{order['id']}", disabled=order["status"] == "Completed"):
            order["status"] = "Cancelled"
            order["delivery_status"] = "Cancelled"
            order["cancellation_reason"] = reason
            st.rerun()
        if distribute_col.button("Mark as Distributed", key=f"distribute-{order['id']}", disabled=not can_distribute):
            order["status"] = "Completed"
            order["distributed"] = True
            st.rerun()

    st.dataframe(
        [
            order_summary(order)
            for order in st.session_state.orders
            if order["assigned_ngo"] == ngo_name
        ],
        use_container_width=True,
    )
