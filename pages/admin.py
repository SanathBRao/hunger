import streamlit as st
from utils import show_map

def show(user):
    st.title("Admin Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", len(st.session_state.orders))
    col2.metric("Pending", sum(order["status"] == "Pending" for order in st.session_state.orders))
    col3.metric("Accepted", sum(order["status"] == "Accepted" for order in st.session_state.orders))
    col4.metric("Total Meals", sum(order["food_qty"] for order in st.session_state.orders))

    action1, action2, action3 = st.columns(3)
    if action1.button("Mark Expired"):
        for order in st.session_state.orders:
            if order["expiry"] <= 0 and order["status"] != "Expired":
                order["status"] = "Expired"
        st.rerun()

    if action2.button("Run Matching"):
        for order in sorted(st.session_state.orders, key=lambda item: item["expiry"]):
            if order["status"] == "Pending":
                order["status"] = "Assigned"
                order["assigned_ngo"] = "Auto Assigned NGO"
        st.rerun()

    if action3.button("Clean Expired"):
        st.session_state.orders[:] = [
            order for order in st.session_state.orders if order["status"] != "Expired"
        ]
        st.rerun()

    st.subheader("All Orders")
    st.dataframe(st.session_state.orders, use_container_width=True)

    st.subheader("Map View")
    show_map(st.session_state.orders)
