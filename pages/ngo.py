import streamlit as st
from database import get_connection

def show(user):
    st.title("NGO Dashboard")

    demand = st.number_input("Food Needed")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    lat = st.number_input("Latitude")
    lon = st.number_input("Longitude")

    if st.button("Request Food"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO requests (user_id, demand, priority, lat, lon) VALUES (?, ?, ?, ?, ?)",
                  (user[0], demand, priority, lat, lon))
        conn.commit()
        conn.close()
        st.success("Request Sent")

    conn = get_connection()
    requests = conn.execute("SELECT * FROM requests WHERE user_id=?", (user[0],)).fetchall()

    st.write("Your Requests")
    st.dataframe(requests)