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
    # Define service access rules
    service_access = {
        "Language Translation": {"roles": ["Editor"], "licenses": ["Enterprise"]},
        "Sentiment Analysis": {"roles": ["Viewer"], "licenses": ["Teams"]},
        "Image Classification": {"roles": ["Admin"], "licenses": ["Teams"]},
        "Agentic Product Search": {"roles": ["Admin"], "licenses": ["Basic"]},
    }
    user_role = st.session_state.get("role")
    user_license = st.session_state.get("license")
    all_services = list(service_access.keys())
    selected_service = st.selectbox("Choose a service:", all_services, key="service_selectbox")
    if st.button("Go", key="service_go_btn"):
        access = service_access[selected_service]
        if user_role in access["roles"] and user_license in access["licenses"]:
            st.session_state.page = selected_service
            st.rerun()
        else:
            needed_roles = ", ".join(access["roles"])
            needed_licenses = ", ".join(access["licenses"])
            st.error("You do not have access to this service.")
            st.info(f"Current role: {user_role}\nCurrent license: {user_license}")
            st.info(f"Required role(s): {needed_roles}\nRequired license(s): {needed_licenses}")
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
    elif st.session_state.page == "Language Translation":
        LanguageTranslation.app()
    elif st.session_state.page == "Sentiment Analysis":
        SentimentAnalysis.app()
    elif st.session_state.page == "Image Classification":
        ImageClassification.app()
    elif st.session_state.page == "Agentic Product Search":
        Agentic_Product_Search.app()