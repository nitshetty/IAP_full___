import streamlit as st
import requests
from utils.config import BACKEND_URL

def app():
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
                st.error(response.json()["detail"])

# Do not auto-run the signup page unless explicitly called from app.py