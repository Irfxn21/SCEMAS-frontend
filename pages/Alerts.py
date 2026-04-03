import streamlit as st
import pandas as pd

from clients.AlertClient import get_alert_rule, get_alerts, update_alert
from clients.SensorClient import get_sensor_data_by_id
from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar
from datetime import datetime


# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")

st.session_state.page = "alerts"

initialize()
render_sidebar()

st.title('🚨 Alerts')
st.caption('View and manage alerts.')

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filterCols1 = st.columns(4)

start_time = filterCols1[0].datetime_input("Start", value=None)
end_time = filterCols1[1].datetime_input("End", value=None)
country = filterCols1[2].text_input("Country")
city = filterCols1[3].text_input("City")

filterCols2 = st.columns(3)

sensor_type = filterCols2[0].selectbox(
    "Sensor",
    options=[None] + list(SensorType),
    format_func=lambda x: x.value if x else "All"
)

severity = filterCols2[1].selectbox(
    "Severity",
    options=[None] + list(AlertSeverity),
    format_func=lambda x: x.value if x else "All"
)

status = filterCols2[2].selectbox(
    "Status",
    options=[None] + list(AlertStatus),
    index=1,
    format_func=lambda x: x.value if x else "All"
)

# -----------------------
# Fetch data
# -----------------------
st.divider()
st.subheader("Results")

if st.session_state.alerts_data == None:
    try:
        st.session_state["alerts_data"] = get_alerts()
    except:
        st.error("Failed to fetch alerts.")
        st.stop()

alerts = st.session_state["alerts_data"]

if not alerts:
    st.info("No alerts available.")
    st.stop()


df = pd.DataFrame([a.__dict__ for a in alerts])

df["time"] = pd.to_datetime(df["time"], unit="s")


# -----------------------
# Apply Filters
# -----------------------
filtered_df = df.copy()

if start_time:
    filtered_df = filtered_df[
        filtered_df["time"] >= pd.to_datetime(start_time)
    ]

if end_time:
    filtered_df = filtered_df[
        filtered_df["time"] <= pd.to_datetime(end_time)
    ]

if sensor_type:
    filtered_df = filtered_df[
        filtered_df["sensor_type"] == sensor_type
    ]

if severity:
    filtered_df = filtered_df[
        filtered_df["severity"] == severity
    ]

if status:
    filtered_df = filtered_df[
        filtered_df["status"] == status
    ]

if country:
    filtered_df = filtered_df[
        filtered_df["country"].str.contains(country, case=False, na=False)
    ]

if city:
    filtered_df = filtered_df[
        filtered_df["city"].str.contains(city, case=False, na=False)
    ]


# -----------------------
# Display Results
# -----------------------
if filtered_df.empty:
    st.warning("No alerts match the selected filters.")
else:
    display_df = filtered_df[
        [
            "status",
            "severity",
            "sensor_type",
            "rule_name",
            "time",
            "country",
            "city",
        ]
    ].copy()

    display_df["sensor_type"] = display_df["sensor_type"].apply(lambda x: x.value)
    display_df["severity"] = display_df["severity"].apply(lambda x: x.value)
    display_df["status"] = display_df["status"].apply(lambda x: x.value)

    # -----------------------
    # Selectable DataFrame
    # -----------------------
    event = st.dataframe(
        display_df,
        width='stretch',
        on_select="rerun",
        selection_mode="single-row",
    )

    prev_selected = st.session_state.get("alerts_selected_alert")

    if event.selection["rows"]:
        selected_index = event.selection["rows"][0]
        new_selected = filtered_df.iloc[selected_index]

        if prev_selected is None or prev_selected.alert_id != new_selected.alert_id:
            st.session_state["alerts_show_dialog"] = False

        st.session_state["alerts_selected_alert"] = new_selected
    else:
        # Selection cleared → close dialog
        st.session_state["alerts_selected_alert"] = None
        st.session_state["alerts_show_dialog"] = False

    # -----------------------
    # Action Button
    # -----------------------
    if st.session_state["alerts_selected_alert"] is not None:
        st.success(
            f"Selected: {st.session_state['alerts_selected_alert']['rule_name']}"
        )

        if st.button("Manage Alert"):
            st.session_state["alerts_show_dialog"] = True


# -----------------------
# Dialog
# -----------------------
if st.session_state.get("alerts_show_dialog", False):

    alert = st.session_state.get("alerts_selected_alert")

    @st.dialog("Manage Alert", width="medium")
    def show_alert_dialog():
        st.caption("Update alert status and/or severity")

        if alert is not None:

            col1, col2 = st.columns(2)

            severity_options = list(AlertSeverity)
            status_options = list(AlertStatus)

            severity = col1.selectbox(
                "Severity",
                options=severity_options,
                format_func=lambda x: x.value,
                width='stretch',
                index=severity_options.index(alert.severity) if alert.severity in severity_options else 0
            )

            status = col2.selectbox(
                "Status",
                options=status_options,
                format_func=lambda x: x.value,
                width='stretch',
                index=status_options.index(alert.status) if alert.status in status_options else 0
            )

            if st.button("Submit", width='stretch'):
                try:
                    update_alert(
                        alert_id=alert.alert_id,
                        alert_status=status.value,
                        alert_severity=severity.value
                    )
                    st.session_state["refresh_alerts"] = True
                    st.session_state.toast = {
                        "message": f"Successfully updated alert status and/or severity",
                        "icon": ":material/check:"
                    }
                except Exception:
                    st.session_state.toast = {
                        "message": f"Failed to update alert status and/or severity",
                        "icon": ":material/error:"
                    }
                    
                st.session_state["alerts_show_dialog"] = False
                st.rerun()

            st.divider()

            def format_ts(ts: int):
                try:
                    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    return ts

            with st.expander("📝 View Alert Rule", expanded=False):
                try:
                    alert_rule = get_alert_rule(alert.rule_id).__dict__

                    alert_rule["created_at"] = format_ts(alert_rule["created_at"])
                    alert_rule["updated_at"] = format_ts(alert_rule["updated_at"])
                    alert_rule["sensor_type"] = alert_rule["sensor_type"].value
                    alert_rule["operator"] = alert_rule["operator"].value
                    alert_rule["location"] = {
                        "longitude": alert_rule["location"].longitude,
                        "latitude": alert_rule["location"].latitude,
                    }

                    st.json(alert_rule)

                except Exception:
                    st.error("failed to fetch data")

            with st.expander("📡 View Sensor Data", expanded=False):
                try:
                    sensor_dict = get_sensor_data_by_id(alert.sensor_id).__dict__

                    sensor_dict["time"] = format_ts(sensor_dict["time"])
                    sensor_dict["sensor_type"] = sensor_dict["sensor_type"].value
                    sensor_dict["location"] = {
                        "longitude": sensor_dict["location"].longitude,
                        "latitude": sensor_dict["location"].latitude,
                    }

                    st.json(sensor_dict)

                except Exception:
                    st.error("failed to fetch data")

    show_alert_dialog()