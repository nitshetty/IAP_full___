import requests
import streamlit as st

from screens import (
    Home,
    Login,
    Signup,
    ForgotPassword,
    ResetPassword,
    LanguageTranslation,
    SentimentAnalysis,
    ImageClassification,
    Agentic_Product_Search
)

st.set_page_config(page_title="AI Use Case Portal", layout="wide")

# Initialize session state for authentication and routing
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Setting default to Home
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def make_request(data):
    response = requests.post("http://backend:8000/endpoint", json=data)
    return response

# Home page
if st.session_state.page == "Home":
    st.title("Welcome to the AI Use Case Portal")
    st.write("")
    col1, col2, col3 = st.columns([8,1,1])
    with col2:
        if st.button("Login", key="home_login_btn"):
            st.session_state.page = "Login"
            st.rerun()
    with col3:
        if st.button("Signup", key="home_signup_btn"):
            st.session_state.page = "Signup"
            st.rerun()
    st.stop()

# Routing for Login, Signup, Forgot/Reset Password
if st.session_state.page == "Login":
    Login.app()
elif st.session_state.page == "Signup":
    Signup.app()
elif st.session_state.page == "Forgot Password":
    ForgotPassword.app()
elif st.session_state.page == "Reset Password":
    ResetPassword.app()

# Service Selection page after login
if st.session_state.get("authenticated", False) and st.session_state.page == "ServiceSelection":
    st.title("Select a Service")
    service_options = [
        "Language Translation",
        "Sentiment Analysis",
        "Image Classification",
        "Agentic Product Search"
    ]
    selected_service = st.selectbox("Choose a service:", service_options, key="service_selectbox")
    if st.button("Go", key="service_go_btn"):
        st.session_state.page = selected_service
        st.rerun()
    st.stop()

# Use case routing (only if authenticated)
def logout_button_footer():
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([8,1,1])
    with col1:
        st.write("")
    with col2:
        st.write("")
    with col3:
        if st.button("Logout", key="logout_btn_footer"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.page = "Login"
            st.rerun()

if st.session_state.get("authenticated", False):
    if st.session_state.page == "Home":
        Home.app()
        logout_button_footer()
    elif st.session_state.page == "Language Translation":
        LanguageTranslation.app()
        logout_button_footer()
    elif st.session_state.page == "Sentiment Analysis":
        SentimentAnalysis.app()
        logout_button_footer()
    elif st.session_state.page == "Image Classification":
        ImageClassification.app()
        logout_button_footer()
    elif st.session_state.page == "Agentic Product Search":
        Agentic_Product_Search.app()