import streamlit as st
from datetime import datetime

from clients.AlertClient import (
    get_all_alert_rules,
    create_alert_rule,
    delete_alert_rule,
)
from models.SensorType import SensorType
from models.ComparisonOperator import ComparisonOperator
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "alert_rules"

initialize()
render_sidebar()

st.title('📝 Alert Rules')
st.caption('Create, view, and delete alert rules that trigger notifications when sensor thresholds are breached.')

# -----------------------
# Session State
# -----------------------
if "alert_rules_data" not in st.session_state or st.session_state.get("refresh_alert_rules"):
    try:
        st.session_state["alert_rules_data"] = get_all_alert_rules()
        st.session_state["refresh_alert_rules"] = False
    except Exception:
        st.error("Failed to fetch alert rules.")
        st.stop()

# -----------------------
# Create Alert Rule Dialog
# -----------------------
@st.dialog("Create Alert Rule", width="large")
def create_rule_dialog():
    st.caption("Define a new rule to trigger alerts when sensor readings cross a threshold.")

    col1, col2 = st.columns(2)

    name = col1.text_input("Rule Name")

    sensor_type = col2.selectbox(
        "Sensor Type",
        options=list(SensorType),
        format_func=lambda x: x.value
    )

    col3, col4 = st.columns(2)

    operator = col3.selectbox(
        "Operator",
        options=list(ComparisonOperator),
        format_func=lambda x: x.value.replace("_", " ").title()
    )

    threshold = col4.number_input("Threshold Value", value=0.0, step=0.1)

    col5, col6, col7 = st.columns(3)

    latitude = col5.number_input("Latitude", value=43.6532, format="%.4f")
    longitude = col6.number_input("Longitude", value=-79.3832, format="%.4f")
    radius = col7.number_input("Radius (km)", value=10.0, step=0.5, min_value=0.1)

    st.write("")

    if st.button("Create Rule", use_container_width=True):
        if not name:
            st.warning("Rule name cannot be empty.")
            return

        try:
            create_alert_rule(
                name=name,
                threshold=threshold,
                operator=operator.value,
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                sensor_type=sensor_type.value
            )
            st.session_state["refresh_alert_rules"] = True
            st.session_state.toast = {
                "message": f"Alert rule '{name}' created successfully.",
                "icon": ":material/check:"
            }
        except Exception:
            st.session_state.toast = {
                "message": "Failed to create alert rule.",
                "icon": ":material/error:"
            }
        st.rerun()


# -----------------------
# Header Row
# -----------------------
header_col1, header_col2 = st.columns([5, 1])

with header_col2:
    st.write("")
    if st.button("＋ Create Rule", use_container_width=True):
        create_rule_dialog()

st.divider()

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filter_cols = st.columns(2)

sensor_filter = filter_cols[0].selectbox(
    "Filter by Sensor Type",
    options=[None] + list(SensorType),
    format_func=lambda x: x.value if x else "All"
)

search = filter_cols[1].text_input("Search by Rule Name")

st.divider()

# -----------------------
# Results
# -----------------------
rules = st.session_state["alert_rules_data"]

filtered_rules = rules

if sensor_filter:
    filtered_rules = [r for r in filtered_rules if r.sensor_type == sensor_filter]

if search:
    filtered_rules = [r for r in filtered_rules if search.lower() in r.name.lower()]

st.subheader("Results")

if not filtered_rules:
    st.info("No alert rules found." if not rules else "No rules match the selected filters.")
    st.stop()

st.caption(f"Showing **{len(filtered_rules)}** rule(s)")

# -----------------------
# Sensor Icons
# -----------------------
SENSOR_ICONS = {
    SensorType.AIR_QUALITY: "🌬️",
    SensorType.NOISE: "🔊",
    SensorType.TEMPERATURE: "🌡️",
    SensorType.HUMIDITY: "💧",
}

def format_ts(ts: int) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)

# -----------------------
# Rule Cards
# -----------------------
for rule in filtered_rules:
    icon = SENSOR_ICONS.get(rule.sensor_type, "📡")

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 3, 1])

        with col1:
            st.markdown(f"**{icon} {rule.name}**")
            st.caption(
                f"📡 {rule.sensor_type.value.title()} · "
                f"Operator: `{rule.operator.value.replace('_', ' ').title()}` · "
                f"Threshold: `{rule.threshold}`"
            )
            st.caption(f"Author: `{rule.author_id}`")

        with col2:
            st.caption(
                f"📍 Lat: `{rule.location.latitude:.4f}`, "
                f"Lon: `{rule.location.longitude:.4f}` · "
                f"Radius: `{rule.radius} km`"
            )
            st.caption(
                f"Created: `{format_ts(rule.created_at)}` · "
                f"Updated: `{format_ts(rule.updated_at)}`"
            )

        with col3:
            if st.button("🗑️ Delete", key=f"delete_rule_{rule.rule_id}", use_container_width=True):
                try:
                    delete_alert_rule(rule.rule_id)
                    st.session_state["refresh_alert_rules"] = True
                    st.session_state.toast = {
                        "message": f"Rule '{rule.name}' deleted.",
                        "icon": ":material/check:"
                    }
                except Exception:
                    st.session_state.toast = {
                        "message": f"Failed to delete rule '{rule.name}'.",
                        "icon": ":material/error:"
                    }
                st.rerun()
