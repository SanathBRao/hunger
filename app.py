import streamlit as st
from auth import login, signup
from database import init_db

init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "orders" not in st.session_state:
    st.session_state.orders = []

st.set_page_config(layout="wide")

def login_page():
    st.title("Zero Hunger System")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["Admin", "NGO", "Donor"])

        if st.button("Signup"):
            if signup(u, p, role):
                st.success("Account created")
            else:
                st.error("User exists")

def main_app():
    user = st.session_state.user
    role = user[3]

    st.sidebar.write(f"Logged in as: {role}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    if role == "Admin":
        from pages import admin
        admin.show(user)

    elif role == "NGO":
        from pages import ngo
        ngo.show(user)

    elif role == "Donor":
        from pages import donor
        donor.show(user)

if st.session_state.user is None:
    login_page()
else:
    main_app()
