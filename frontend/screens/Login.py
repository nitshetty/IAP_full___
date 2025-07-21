import streamlit as st
import requests
from utils.auth import save_token
from utils.config import BACKEND_URL
import jwt

def app():
    st.title("Login")

    # Inputs
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Buttons
    col1, col2, col3 = st.columns([2, 6, 2])  # Wider center area
    with col1:
        login_clicked = st.button("Login", use_container_width=True)
    with col3:
        forgot_clicked = st.button("Forgot Password?", use_container_width=True)

    # Logic
    if login_clicked:
        response = requests.post(f"{BACKEND_URL}/login", data={"username": email, "password": password})
        if response.status_code == 200:
            token_data = response.json()
            try:
                decoded = jwt.decode(token_data['access_token'], options={"verify_signature": False})
                role = decoded.get("role")
                license = decoded.get("license")
            except Exception as e:
                role = None
                license = None
            save_token(token_data['access_token'], role, license)
            st.success(f"Login successful. Role: {role}, License: {license}")
            st.session_state.authenticated = True
            st.session_state.page = "ServiceSelection"
            st.rerun()
        else:
            st.error("Invalid credentials")

    if forgot_clicked:
        st.session_state.page = "Forgot Password"
        st.rerun()