import streamlit as st
import requests
from utils.config import BACKEND_URL

def save_token(token, role, license):
    st.session_state.access_token = token
    st.session_state.role = role
    st.session_state.license = license

def is_authenticated():
    return st.session_state.get("access_token") is not None

def has_role(required_roles):
    return st.session_state.get("role") in required_roles

def has_license(required_licenses):
    return st.session_state.get("license") in required_licenses