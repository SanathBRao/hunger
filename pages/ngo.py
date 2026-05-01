import streamlit as st

def show(user):
    st.title("NGO Dashboard")
    ngo_name = user[1]

    st.subheader("Available Food")
    for order in st.session_state.orders:
        if order["status"] != "Pending":
            continue

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write(f"Donor: {order['donor_name']}")
        col2.write(f"Qty: {order['food_qty']}")
        col3.write(f"Expiry: {order['expiry']} hrs")
        if col4.button("Accept", key=f"accept-{order['id']}"):
            order["status"] = "Accepted"
            order["assigned_ngo"] = ngo_name
            st.rerun()

    st.subheader("Accepted Orders")
    st.dataframe(
        [
            order
            for order in st.session_state.orders
            if order["assigned_ngo"] == ngo_name and order["status"] in ("Accepted", "Assigned")
        ],
        use_container_width=True,
    )
