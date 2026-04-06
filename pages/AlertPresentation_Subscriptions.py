import streamlit as st

from clients.AlertClient import (
    get_all_alert_rules,
    get_my_subscriptions,
    subscribe_to_alert,
    unsubscribe_from_alert,
)
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "subscriptions"

initialize()
render_sidebar()

st.title('📧 Subscriptions')
st.caption('Manage your alert subscriptions. Subscribe to rules to receive notifications when thresholds are breached.')

# -----------------------
# Load Data
# -----------------------
try:
    my_subscriptions = get_my_subscriptions()
    subscribed_rule_ids = {s.rule_id for s in my_subscriptions}
except Exception:
    st.error("Failed to fetch your subscriptions.")
    st.stop()

try:
    all_rules = get_all_alert_rules()
except Exception:
    st.error("Failed to fetch alert rules.")
    st.stop()

# -----------------------
# My Subscriptions
# -----------------------
st.subheader("📋 My Subscriptions")

if not my_subscriptions:
    st.info("You are not subscribed to any alert rules yet.")
else:
    for sub in my_subscriptions:
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(f"**{sub.rule_name}**")
            st.caption(f"Rule ID: `{sub.rule_id}` · Subscription ID: `{sub.subscription_id}`")

        with col2:
            if st.button("Unsubscribe", key=f"unsub_{sub.subscription_id}", use_container_width=True):
                try:
                    unsubscribe_from_alert(sub.rule_id)
                    st.session_state.toast = {
                        "message": f"Unsubscribed from {sub.rule_name}.",
                        "icon": ":material/check:"
                    }
                except Exception:
                    st.session_state.toast = {
                        "message": f"Failed to unsubscribe from {sub.rule_name}.",
                        "icon": ":material/error:"
                    }
                st.rerun()

st.divider()

# -----------------------
# Available Rules
# -----------------------
st.subheader("🔔 Available Alert Rules")
st.caption("Browse all active alert rules and subscribe to ones relevant to you.")

if not all_rules:
    st.info("No alert rules are currently available.")
else:
    # -----------------------
    # Filter
    # -----------------------
    filter_cols = st.columns(2)

    sensor_filter = filter_cols[0].selectbox(
        "Filter by Sensor Type",
        options=[None] + list(SensorType),
        format_func=lambda x: x.value if x else "All"
    )

    search = filter_cols[1].text_input("Search by Rule Name")

    filtered_rules = all_rules

    if sensor_filter:
        filtered_rules = [r for r in filtered_rules if r.sensor_type == sensor_filter]

    if search:
        filtered_rules = [r for r in filtered_rules if search.lower() in r.name.lower()]

    if not filtered_rules:
        st.warning("No rules match the selected filters.")
    else:
        for rule in filtered_rules:
            is_subscribed = rule.rule_id in subscribed_rule_ids

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{rule.name}**")
                    st.caption(
                        f"📡 {rule.sensor_type.value.title()} · "
                        f"Threshold: `{rule.threshold}` · "
                        f"Operator: `{rule.operator.value}`"
                    )

                with col2:
                    st.caption(
                        f"📍 Lat: `{rule.location.latitude:.4f}`, "
                        f"Lon: `{rule.location.longitude:.4f}` · "
                        f"Radius: `{rule.radius} km`"
                    )

                with col3:
                    if is_subscribed:
                        st.success("Subscribed")
                        if st.button("Unsubscribe", key=f"unsub_rule_{rule.rule_id}", use_container_width=True):
                            try:
                                unsubscribe_from_alert(rule.rule_id)
                                st.session_state.toast = {
                                    "message": f"Unsubscribed from {rule.name}.",
                                    "icon": ":material/check:"
                                }
                            except Exception:
                                st.session_state.toast = {
                                    "message": f"Failed to unsubscribe.",
                                    "icon": ":material/error:"
                                }
                            st.rerun()
                    else:
                        if st.button("Subscribe", key=f"sub_rule_{rule.rule_id}", use_container_width=True):
                            try:
                                subscribe_to_alert(rule.rule_id)
                                st.session_state.toast = {
                                    "message": f"Subscribed to {rule.name}.",
                                    "icon": ":material/check:"
                                }
                            except Exception:
                                st.session_state.toast = {
                                    "message": f"Failed to subscribe.",
                                    "icon": ":material/error:"
                                }
                            st.rerun()
