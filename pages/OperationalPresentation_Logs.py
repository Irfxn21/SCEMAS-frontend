import streamlit as st
import pandas as pd
from datetime import datetime

from clients.OperationalClient import get_logs
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "logs"

initialize()
render_sidebar()

st.title('📄 Logs')
st.caption('View system audit logs for user actions and events.')

# -----------------------
# Load Logs
# -----------------------
if "logs_data" not in st.session_state or st.session_state.get("refresh_logs"):
    try:
        st.session_state["logs_data"] = get_logs()
        st.session_state["refresh_logs"] = False
    except Exception:
        st.error("Failed to fetch logs.")
        st.stop()

logs = st.session_state["logs_data"]

if not logs:
    st.info("No logs available.")
    st.stop()

# -----------------------
# Refresh Button
# -----------------------
header_col1, header_col2 = st.columns([5, 1])

with header_col2:
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state["refresh_logs"] = True
        st.rerun()

# -----------------------
# Summary Metrics
# -----------------------
st.subheader("📊 Overview")

metric_cols = st.columns(3)

metric_cols[0].metric("Total Logs", len(logs))

unique_users = len({log.user_id for log in logs})
metric_cols[1].metric("Unique Users", unique_users)

from collections import Counter
most_common_msg, most_common_count = Counter(
    log.log_message for log in logs
).most_common(1)[0]
metric_cols[2].metric("Most Common Event", most_common_msg, help=f"Occurred {most_common_count} time(s)")

st.divider()

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filter_cols = st.columns(3)

search_email = filter_cols[0].text_input("Search by Email")
search_message = filter_cols[1].text_input("Search by Message")

filter_cols2 = st.columns(2)
start_time = filter_cols2[0].datetime_input("Start", value=None)
end_time = filter_cols2[1].datetime_input("End", value=None)

st.divider()

# -----------------------
# Build DataFrame
# -----------------------
df = pd.DataFrame([log.__dict__ for log in logs])
df["time"] = pd.to_datetime(df["time"], unit="s")

# -----------------------
# Apply Filters
# -----------------------
filtered_df = df.copy()

if search_email:
    filtered_df = filtered_df[
        filtered_df["email"].str.contains(search_email, case=False, na=False)
    ]

if search_message:
    filtered_df = filtered_df[
        filtered_df["log_message"].str.contains(search_message, case=False, na=False)
    ]

if start_time:
    filtered_df = filtered_df[
        filtered_df["time"] >= pd.to_datetime(start_time)
    ]

if end_time:
    filtered_df = filtered_df[
        filtered_df["time"] <= pd.to_datetime(end_time)
    ]

# -----------------------
# Results
# -----------------------
st.subheader("Results")

if filtered_df.empty:
    st.warning("No logs match the selected filters.")
    st.stop()

st.caption(f"Showing **{len(filtered_df)}** of **{len(logs)}** logs")

display_df = filtered_df[
    ["time", "email", "log_message", "user_id", "log_id"]
].copy()

display_df = display_df.rename(columns={
    "time": "Time",
    "email": "Email",
    "log_message": "Message",
    "user_id": "User ID",
    "log_id": "Log ID",
})

display_df = display_df.sort_values("Time", ascending=False)

event = st.dataframe(
    display_df,
    width="stretch",
    on_select="rerun",
    selection_mode="single-row",
    hide_index=True,
)

# -----------------------
# Detail Expander on Select
# -----------------------
if event.selection["rows"]:
    selected_index = event.selection["rows"][0]
    selected_row = filtered_df.iloc[selected_index]

    st.divider()
    st.subheader("🔍 Log Detail")

    detail_cols = st.columns(2)

    with detail_cols[0]:
        st.markdown(f"**Log ID:** `{selected_row['log_id']}`")
        st.markdown(f"**User ID:** `{selected_row['user_id']}`")
        st.markdown(f"**Email:** `{selected_row['email']}`")

    with detail_cols[1]:
        st.markdown(f"**Message:** {selected_row['log_message']}")
        st.markdown(f"**Time:** `{selected_row['time'].strftime('%Y-%m-%d %H:%M:%S')}`")
