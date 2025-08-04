# auth.py
import streamlit as st
from db import add_user, validate_user

def login_form():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        name = validate_user(username, password)
        if name:
            st.session_state.authenticated = True
            st.session_state.name = name
            st.success(f"Welcome back, {name}!")
            st.rerun()

        else:
            st.error("Invalid username or password")

def signup_form():
    st.subheader("📝 Sign Up")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        success = add_user(username, name, email, password)
        if success:
            st.success("Account created! Please log in.")
        else:
            st.error("Username or Email already exists")
