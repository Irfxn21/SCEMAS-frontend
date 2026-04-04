import streamlit as st

from models.AccountRole import AccountRole
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

st.set_page_config(layout="centered")
st.session_state.page = "home"


st.set_page_config(layout="centered")
initialize()
render_sidebar()

st.title('🏠 SCEMAS')
st.caption('🚀 Smart City Environmental Monitoring & Alert System')

st.write("Platform designed to monitor environmental data, generate alerts, and provide actionable insights for smart city infrastructure.")

st.subheader("Quick Links")

if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR, AccountRole.PUBLIC]:
    st.caption("Public Access")
    st.page_link("pages/AggregatedData.py", label="Aggregated Data", icon="📊", width="stretch")
    st.page_link("pages/Subscriptions.py", label="Subscriptions", icon="📧", width="stretch")

if st.session_state.role in [AccountRole.ADMIN, AccountRole.OPERATOR]:
    st.caption("Operations")
    st.page_link("pages/Visualizations.py", label="Visualizations", icon="🗺️", width="stretch")
    st.page_link("pages/Alerts.py", label="Alerts", icon="🚨", width="stretch")
    st.page_link("pages/Sensors.py", label="Sensors", icon="📡", width="stretch")
    st.page_link("pages/SystemHealth.py", label="System Health", icon="❤️‍🩹", width="stretch")

if st.session_state.role in [AccountRole.ADMIN]:
    st.caption("Administration")
    st.page_link("pages/AlertRules.py", label="Alert Rules", icon="📝", width="stretch")
    st.page_link("pages/Logs.py", label="Logs", icon="📄", width="stretch")
    st.page_link("pages/Accounts.py", label="Accounts", icon="👤", width="stretch")