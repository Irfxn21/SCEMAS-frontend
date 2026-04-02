import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


st.session_state.page = "system_health"

initialize()
render_sidebar()

st.title('❤️‍🩹 System Health')