import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


st.session_state.page = "sensors"

initialize()
render_sidebar()

st.title('📷 Sensors')