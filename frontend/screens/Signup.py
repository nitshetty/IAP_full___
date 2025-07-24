import streamlit as st
import requests
from utils.config import BACKEND_URL

def app():
    col_spacer, col_login = st.columns([8, 2])
    with col_login:
        if st.button("Already have an account?", key="login_btn"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.access_token = None
            st.session_state.page = "Login"
            st.rerun()
    st.title("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    role = st.selectbox("Role", ["Admin", "Editor", "Viewer"], key="signup_role")
    license = st.selectbox("License", ["Basic", "Teams", "Enterprise"], key="signup_license")
    if st.button("Sign Up"):
        missing = []
        if not email:
            missing.append("email")
        if not password:
            missing.append("password")
        if missing:
            if len(missing) == 2:
                st.error("Please provide both email and password.")
            else:
                st.error(f"Please provide your {missing[0]}.")
        else:
            data = {"email": email, "password": password, "role": role, "license": license}
            response = requests.post(f"{BACKEND_URL}/signup", json=data)
            if response.status_code == 200:
                st.success("User registered successfully")
            else:
                st.error(response.json().get("detail", "Signup failed. Please try again."))
