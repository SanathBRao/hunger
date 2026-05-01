import streamlit as st
from datetime import datetime
from utils import order_summary

def show(user):
    st.title("Donor Dashboard")

    qty = st.number_input("Food Quantity", min_value=1, step=1)
    expiry = st.number_input("Expiry (hrs)", min_value=0.0, step=0.5)
    x = st.number_input("Location X")
    y = st.number_input("Location Y")

    if st.button("Add Donation"):
        next_id = max([order["id"] for order in st.session_state.orders], default=0) + 1
        st.session_state.orders.append({
            "id": next_id,
            "donor_name": user[1],
            "food_qty": int(qty),
            "expiry": float(expiry),
            "location": (x, y),
            "status": "Pending",
            "assigned_ngo": None,
            "created_at": datetime.now(),
        })
        st.rerun()

    st.subheader("Your Donations")
    st.dataframe(
        [
            order_summary(order)
            for order in st.session_state.orders
            if order["donor_name"] == user[1]
        ],
        use_container_width=True,
    )
