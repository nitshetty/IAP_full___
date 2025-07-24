import streamlit as st
import requests
from utils.config import BACKEND_URL

def app():
    col_spacer, col_login = st.columns([8, 2])
    with col_login:
        if st.button("Login", key="login_btn"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.access_token = None
            st.session_state.page = "Login"
            st.rerun()
    st.title("Reset Password")
    email = st.text_input("Email", key="reset_password_email")
    token = st.text_input("Reset Token", key="reset_token")
    new_password = st.text_input("New Password", type="password", key="reset_password_new_password")
    if st.button("Reset"):
        if not email and not token and not new_password:
            st.error("Email, Reset Token, and New Password cannot be empty.please provide them")
            return
        elif not email and not new_password:
            st.error("Email and New Password cannot be empty.please provide them")
            return
        elif not email:
            st.error("Email cannot be empty.please provide it")
            return
        elif not token:
            st.error("Reset Token cannot be empty.please provide it")
            return
        elif not new_password:
            st.error("New Password cannot be empty.please provide it")
            return
        elif not new_password and not token:
            st.error("Reset Token and New Password cannot be empty.please provide them")
            return
        elif not email and not token:
            st.error("Email and Reset Token cannot be empty.please provide them")
            return
        payload = {"email": email, "token": token, "new_password": new_password}
        res = requests.post(f"{BACKEND_URL}/reset-password", json=payload)
        if res.status_code == 200:
            st.success("Password reset successful")
        else:
            st.error(res.json()["detail"])


app()