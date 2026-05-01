import streamlit as st
from database import get_connection

def show(user):
    st.title("Donor Dashboard")

    qty = st.number_input("Food Quantity")
    expiry = st.number_input("Expiry (hrs)")
    lat = st.number_input("Latitude")
    lon = st.number_input("Longitude")

    if st.button("Add Donation"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO donations (user_id, quantity, expiry, lat, lon) VALUES (?, ?, ?, ?, ?)",
                  (user[0], qty, expiry, lat, lon))
        conn.commit()
        conn.close()
        st.success("Donation Added")

    conn = get_connection()
    donations = conn.execute("SELECT * FROM donations WHERE user_id=?", (user[0],)).fetchall()

    st.write("Your Donations")
    st.dataframe(donations)