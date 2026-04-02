import streamlit as st
import time
from clients.AlertClient import get_alerts
from utils.Initialize import initialize
from clients.FirebaseClient import login, signup, logout
from utils.Sidebar import render_sidebar

st.session_state.page = "app"

initialize()

def clear_login_fields():
    st.session_state.login_email_key = f"login_email_{time.time()}"
    st.session_state.login_password_key =  f"login_password_{time.time()}"
    st.rerun()

def clear_signup_fields():
    st.session_state.signup_email_key = f"signup_email_{time.time()}"
    st.session_state.signup_password_key =  f"signup_password_{time.time()}"
    st.rerun()

if st.session_state.logged_in == False:
    st.title('SCEMAS')
    st.caption('🚀 Smart City Environmental Monitoring & Alert System')

    login_tab, signup_tab = st.tabs(["🔑 Login", "📝 Sign Up"])

    # LOGIN TAB
    with login_tab:
        st.subheader("Login")

        email = st.text_input("📧 Email", key=st.session_state.login_email_key)
        password = st.text_input("🔐 Password", type="password", key=st.session_state.login_password_key)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Submit", use_container_width=True, key="login_button"):
                if email != "" and password != "":
                    login(email, password)
                    clear_login_fields()
                else:
                    st.toast("Input fields cannot be empty.", icon=":material/warning:")
        with col2:
            if st.button("Clear", use_container_width=True, key="login_clear_button"):
                clear_login_fields()

    # SIGNUP TAB
    with signup_tab:
        st.subheader("Sign Up")

        email = st.text_input("📧 Email", key=st.session_state.signup_email_key)
        password = st.text_input("🔐 Password", type="password", key=st.session_state.signup_password_key)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Submit", use_container_width=True, key="signup_button"):
                if email != "" and password != "":
                    signup(email, password)
                    clear_signup_fields()
                else:
                    st.toast("Input fields cannot be empty.", icon=":material/warning:")
        
        with col2:
            if st.button("Clear", use_container_width=True, key="signup_clear_button"):
                clear_signup_fields()

else:
    st.switch_page("pages/Home.py")