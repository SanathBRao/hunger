import streamlit as st
from database import get_connection
from utils import show_map

def show(user):
    st.title("Admin Dashboard")

    conn = get_connection()

    donations = conn.execute("SELECT * FROM donations").fetchall()
    requests = conn.execute("SELECT * FROM requests").fetchall()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Donations", len(donations))
    col2.metric("Total Requests", len(requests))
    col3.metric("Total Meals", sum([d[2] for d in donations]) if donations else 0)

    st.subheader("All Donations")
    st.dataframe(donations)

    st.subheader("All Requests")
    st.dataframe(requests)

    st.subheader("Map View")
    show_map(donations, requests)