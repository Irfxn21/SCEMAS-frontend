import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

st.set_page_config(layout="centered")
st.session_state.page = "system_health"

initialize()
render_sidebar()

st.title('❤️‍🩹 System Health')