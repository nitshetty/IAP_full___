import streamlit as st
import requests
from utils.config import BACKEND_URL

def app():
    st.title("Forgot Password")

    # Email input
    email = st.text_input("Email", key="forgot_email")

    # Button layout: token left, reset right
    col1, col2, col3 = st.columns([3, 4, 3])  # Adjust for spacing

    with col1:
        generate_clicked = st.button("Generate Reset Token", use_container_width=True)
    with col3:
        reset_password_clicked = st.button("Reset Password", use_container_width=True)

    # Logic for generating reset token
    if generate_clicked:
        if not email:
            st.error("Email is required.please provide it.")
        else:
            try:
                res = requests.post(f"{BACKEND_URL}/forgot-password", json={"email": email})
                if res.status_code == 200:
                    reset_token = res.json().get("reset_token")
                    if reset_token:
                        st.success(f"Token generated successfully: {reset_token}")
                    else:
                        st.warning("Token generated, but no token returned.")
                else:
                    st.error(res.json().get("detail", "Failed to generate token."))
            except Exception:
                st.error("Server error. Please try again later.")

    # Logic for navigating to Reset Password
    if reset_password_clicked:
        st.session_state.page = "Reset Password"
        st.rerun()