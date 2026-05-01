import streamlit as st
from database import get_connection
from utils import order_summary, show_map

def show(user):
    st.title("Admin Dashboard")

    expired_orders = [
        order for order in st.session_state.orders if order["status"] == "Expired"
    ]

    if expired_orders:
        st.warning(f"{len(expired_orders)} expired order(s) need attention.")

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

        next_ngo = 0
        for order in sorted(st.session_state.orders, key=lambda item: item["expiry"]):
            if order["status"] == "Pending":
                order["status"] = "Assigned"
                if ngo_names:
                    order["assigned_ngo"] = ngo_names[next_ngo % len(ngo_names)]
                    next_ngo += 1
                else:
                    order["assigned_ngo"] = "Auto Assigned NGO"
        st.rerun()

    if action3.button("Clean Expired/Completed"):
        st.session_state.orders[:] = [
            order
            for order in st.session_state.orders
            if order["status"] not in ("Expired", "Completed")
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

    st.subheader("Map View")
    show_map(st.session_state.orders)
