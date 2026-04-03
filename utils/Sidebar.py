import streamlit as st
from clients.FirebaseClient import logout
from models.AccountRole import AccountRole

@st.dialog("Logout")
def logout_dialog():
    st.write(f"Are you sure you want to log out of the account {st.session_state.user}?")

    if st.button("Logout", key="log_out_button", use_container_width=True):
        logout()
        st.rerun()

def render_sidebar():
    with st.sidebar:
        st.page_link("pages/Home.py", label="Home", icon="🏠")

        if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR, AccountRole.PUBLIC]:
            st.caption("Public Access")
            st.page_link("pages/AggregatedData.py", label="Aggregated Data", icon="📊")
            st.page_link("pages/Subscriptions.py", label="Subscriptions", icon="📧")

        if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR]:
            st.caption("Operations")
            st.page_link("pages/Visualizations.py", label="Visualizations", icon="🗺️")
            st.page_link("pages/Alerts.py", label="Alerts", icon="🚨")
            st.page_link("pages/Sensors.py", label="Sensors", icon="📡")
            st.page_link("pages/SystemHealth.py", label="System Health", icon="❤️‍🩹")

        if st.session_state.role in [AccountRole.ADMIN]:
            st.caption("Administration")
            st.page_link("pages/AlertRules.py", label="Alert Rules", icon="📝")
            st.page_link("pages/Logs.py", label="Logs", icon="📄")
            st.page_link("pages/Accounts.py", label="Accounts", icon="👤")

        st.divider()

        st.caption(f"**User:** {st.session_state.user}")
        st.caption(f"**Role:** {st.session_state.role.value}")

        if st.button("Logout", key="log_out", use_container_width=True):
            logout_dialog()