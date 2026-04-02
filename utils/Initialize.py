import streamlit as st

from models.AccountRole import AccountRole

def initialize():
    st.set_page_config(page_title="SCEMAS")

    if "toast" in st.session_state:
        st.toast(st.session_state.toast["message"], icon=st.session_state.toast["icon"])
        del st.session_state.toast

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'page' not in st.session_state:
        st.session_state.page = None

    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'role' not in st.session_state:
        st.session_state.role = None

    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None

    if 'token' not in st.session_state:
        st.session_state.token = None

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if "login_email_key" not in st.session_state:
        st.session_state.login_email_key = "login_email"

    if "login_password_key" not in st.session_state:
        st.session_state.login_password_key = "login_password"

    if "signup_email_key" not in st.session_state:
        st.session_state.signup_email_key = "signup_email"

    if "signup_password_key" not in st.session_state:
        st.session_state.signup_password_key = "signup_password"

    if "alerts_selected_alert" not in st.session_state:
        st.session_state.alerts_selected_alert = None

    if "alerts_show_dialog" not in st.session_state:
        st.session_state.alerts_show_dialog = None

    if "alerts_data" not in st.session_state:
        st.session_state.alerts_data = None

    if "alerts_selected_index" not in st.session_state:
        st.session_state["alerts_selected_index"] = None

    if "alerts_table_key" not in st.session_state:
        st.session_state["alerts_table_key"] = "alerts_table"

    if "refresh_alerts" not in st.session_state:
        st.session_state["refresh_alerts"] = False

    if (st.session_state.logged_in == False and st.session_state.page != "app"):
        st.switch_page("app.py")

    if (st.session_state.page != "alerts" or st.session_state.refresh_alerts == True):
        st.session_state["refresh_alerts"] = False
        st.session_state.alerts_selected_alert = None
        st.session_state.alerts_show_dialog = None
        st.session_state.alerts_data = None
        st.session_state.alerts_selected_index = None
        st.session_state.alerts_table_key = None