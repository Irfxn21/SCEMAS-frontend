import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


st.session_state.page = "home"


st.set_page_config(layout="centered")
initialize()
render_sidebar()

st.title('🏠 Home')