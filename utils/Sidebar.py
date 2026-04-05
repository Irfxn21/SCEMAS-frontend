import streamlit as st
from clients.FirebaseClient import logout
from models.AccountRole import AccountRole

@st.dialog("Logout")
def logout_dialog():
    st.write(f"Are you sure you want to log out of the account {st.session_state.user}?")

    if st.button("Logout", key="log_out_button", use_container_width=True):
        logout()
        st.rerun()

def render_page_links():
    # ALERTS Section
    alert_pages = []
    if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR]:
        alert_pages.append(("pages/AlertPresentation_Alerts.py", "Alerts", "🚨"))
    if st.session_state.role in [AccountRole.ADMIN]:
        alert_pages.append(("pages/AlertPresentation_AlertRules.py", "Alert Rules", "📝"))
    if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR, AccountRole.PUBLIC]:
        alert_pages.append(("pages/AlertPresentation_Subscriptions.py", "Subscriptions", "📧"))

    if alert_pages:
        st.caption("Alerts")
        for page, label, icon in alert_pages:
            st.page_link(page, label=label, icon=icon, width='stretch')

    # SENSORS Section
    sensor_pages = []
    if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR]:
        sensor_pages.append(("pages/SensorPresentation_Visualizations.py", "Visualizations", "🗺️"))
        sensor_pages.append(("pages/SensorPresentation_Sensors.py", "Sensors", "📡"))
        sensor_pages.append(("pages/SensorPresentation_Predictions.py", "Predictions", "🧠"))
    if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR, AccountRole.PUBLIC]:
        sensor_pages.append(("pages/SensorPresentation_AggregatedData.py", "Aggregated Data", "📊"))

    if sensor_pages:
        st.caption("Sensors")
        for page, label, icon in sensor_pages:
            st.page_link(page, label=label, icon=icon, width='stretch')

    # OPERATIONS Section
    operation_pages = []
    if st.session_state.role in [AccountRole.ADMIN]:
        operation_pages.append(("pages/OperationalPresentation_Logs.py", "Logs", "📄"))
    if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR]:
        operation_pages.append(("pages/OperationalPresentation_SystemHealth.py", "System Health", "❤️‍🩹"))

    if operation_pages:
        st.caption("Operations")
        for page, label, icon in operation_pages:
            st.page_link(page, label=label, icon=icon, width='stretch')

    # ACCOUNTS Section
    account_pages = []
    if st.session_state.role in [AccountRole.ADMIN]:
        account_pages.append(("pages/AccountPresentation_Accounts.py", "Accounts", "👤"))

    if account_pages:
        st.caption("Accounts")
        for page, label, icon in account_pages:
            st.page_link(page, label=label, icon=icon, width='stretch')

def render_sidebar():
    with st.sidebar:
        st.page_link("pages/Home.py", label="Home", icon="🏠")

        render_page_links()
        st.divider()

        st.caption(f"**User:** {st.session_state.user}")
        st.caption(f"**Role:** {st.session_state.role.value}")

        if st.button("Logout", key="log_out", use_container_width=True):
            logout_dialog()