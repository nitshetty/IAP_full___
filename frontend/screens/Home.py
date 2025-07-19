import streamlit as st

def app():
    st.markdown(
        """
        <div style='display:flex; justify-content:center; align-items:center; height: 40vh;'>
            <h1 style="font-size:2.8rem; font-weight:800; text-align:center;">Welcome to the <span style='color:#FFD166;'>AI Use Case Portal</span></h1>
        </div>
        <div style="text-align:center; color:#888; font-size:18px; margin-top:2rem;">
            <em>Start exploring by logging in or signing up!</em>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Login and Signup buttons at the top-right if not authenticated
    if not st.session_state.get("authenticated", False):
        col1, col2, col3 = st.columns([8,1,1])
        with col2:
            if st.button("Login", key="home_login_btn_inline"):
                st.session_state.page = "Login"
                st.rerun()
        with col3:
            if st.button("Signup", key="home_signup_btn_inline"):
                st.session_state.page = "Signup"
                st.rerun()