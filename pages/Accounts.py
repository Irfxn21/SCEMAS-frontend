import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

st.set_page_config(layout="centered")
st.session_state.page = "accounts"

initialize()
render_sidebar()

st.title('👤 Accounts')