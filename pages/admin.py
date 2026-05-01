import streamlit as st
from database import get_connection
from utils import (
    calculate_distance,
    MAX_DELIVERY_DISTANCE,
    delivery_feasibility,
    order_summary,
    show_map,
    sync_order_logistics,
)

def show(user):
    st.title("Admin Dashboard")

    expired_orders = [
        order for order in st.session_state.orders if order["status"] == "Expired"
    ]

    if expired_orders:
        st.warning(f"{len(expired_orders)} expired order(s) need attention.")

    failed_location_orders = []
    for order in st.session_state.orders:
        sync_order_logistics(order)
        if order.get("distance") is not None and order["distance"] > MAX_DELIVERY_DISTANCE:
            failed_location_orders.append(order)

    if failed_location_orders:
        st.error(f"{len(failed_location_orders)} order(s) exceed delivery distance limits.")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", len(st.session_state.orders))
    col2.metric("Pending", sum(order["status"] == "Pending" for order in st.session_state.orders))
    col3.metric("Accepted", sum(order["status"] == "Accepted" for order in st.session_state.orders))
    col4.metric("Assigned", sum(order["status"] == "Assigned" for order in st.session_state.orders))
    col5.metric("Total Meals", sum(order["food_qty"] for order in st.session_state.orders))

    action1, action2, action3 = st.columns(3)
    if action1.button("Mark Expired"):
        for order in st.session_state.orders:
            if order["expiry"] <= 0 and order["status"] in ("Pending", "Accepted", "Assigned"):
                order["status"] = "Expired"
        st.rerun()

    if action2.button("Run Matching"):
        conn = get_connection()
        ngo_names = [
            row[0]
            for row in conn.execute("SELECT username FROM users WHERE role='NGO'").fetchall()
        ]
        conn.close()

        for order in sorted(st.session_state.orders, key=lambda item: item["expiry"]):
            if order["status"] == "Pending":
                sync_order_logistics(order)
                eligible_ngos = []
                for ngo_name in ngo_names:
                    ngo_location = st.session_state.ngo_locations.get(ngo_name)
                    if not ngo_location:
                        continue

                    distance = calculate_distance(order["donor_location"], ngo_location)
                    if distance <= MAX_DELIVERY_DISTANCE and order["expiry"] > 1:
                        eligible_ngos.append((distance, ngo_name, ngo_location))

                if not eligible_ngos:
                    continue

                distance, ngo_name, ngo_location = sorted(eligible_ngos)[0]
                order["status"] = "Assigned"
                order["assigned_ngo"] = ngo_name
                order["ngo_location"] = ngo_location
                order["distance"] = distance
                order["delivery_status"] = "In Transit"
        st.rerun()

    if action3.button("Clean Expired/Completed"):
        st.session_state.orders[:] = [
            order
            for order in st.session_state.orders
            if order["status"] not in ("Expired", "Completed", "Cancelled")
        ]
        st.rerun()

    st.subheader("All Orders")
    st.dataframe(
        [order_summary(order) for order in st.session_state.orders],
        use_container_width=True,
    )

    st.subheader("Expired Orders")
    st.dataframe(
        [order_summary(order) for order in st.session_state.orders if order["status"] == "Expired"],
        use_container_width=True,
    )

    st.subheader("Location-Constrained Deliveries")
    st.dataframe(
        [
            order_summary(order)
            for order in st.session_state.orders
            if delivery_feasibility(order) == "Too far"
        ],
        use_container_width=True,
    )

    st.subheader("Map View")
    show_map(st.session_state.orders)
