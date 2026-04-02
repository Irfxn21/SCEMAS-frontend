import streamlit as st

from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


st.session_state.page = "aggregated_data"

initialize()
render_sidebar()

st.title('📊 Aggregated Data')