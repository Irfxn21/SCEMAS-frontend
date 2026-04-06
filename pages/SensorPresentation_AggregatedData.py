import streamlit as st
import pandas as pd

from clients.SensorClient import get_aggregated_data, get_filtered_sensor_data
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "aggregated_data"

initialize()
render_sidebar()

st.title('📊 Aggregated Data')
st.caption('View aggregated environmental sensor statistics by region and sensor type.')

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

filter_cols = st.columns(4)

country = filter_cols[0].text_input("Country")
city = filter_cols[1].text_input("City")

sensor_type = filter_cols[2].selectbox(
    "Sensor Type",
    options=[None] + list(SensorType),
    format_func=lambda x: x.value if x else "All"
)

filter_cols2 = st.columns(2)
start_time = filter_cols2[0].datetime_input("Start", value=None)
end_time = filter_cols2[1].datetime_input("End", value=None)

submit = st.button("Fetch Data", width='stretch')

st.divider()

# -----------------------
# Fetch + Display
# -----------------------
if submit or "agg_data_loaded" in st.session_state:

    st.session_state["agg_data_loaded"] = True

    start_ts = int(start_time.timestamp()) if start_time else None
    end_ts = int(end_time.timestamp()) if end_time else None
    sensor_type_str = sensor_type.value if sensor_type else None

    try:
        agg = get_aggregated_data(
            country=country or None,
            city=city or None,
            sensor_type=sensor_type_str,
            start_time=start_ts,
            end_time=end_ts
        )
    except Exception:
        st.error("Failed to fetch aggregated data.")
        st.stop()

    if not agg:
        st.info("No aggregated data available.")
        st.stop()

    # -----------------------
    # Summary Cards
    # -----------------------
    st.subheader("📈 Summary Statistics")

    sensor_labels = {
        "air_quality": ("🌬️", "Air Quality", "AQI"),
        "noise": ("🔊", "Noise", "dB"),
        "temperature": ("🌡️", "Temperature", "°C"),
        "humidity": ("💧", "Humidity", "%"),
    }

    cols = st.columns(len(agg))

    for i, (key, stats) in enumerate(agg.items()):
        icon, label, unit = sensor_labels.get(key, ("📡", key.title(), ""))

        with cols[i]:
            st.metric(
                label=f"{icon} {label} — Avg",
                value=f"{stats['avg']} {unit}",
                help=f"Min: {stats['min']} | Max: {stats['max']} | Count: {stats['count']}"
            )
            st.caption(f"Min: **{stats['min']}** · Max: **{stats['max']}** · Readings: **{stats['count']}**")

    st.divider()

    # -----------------------
    # Detail Table
    # -----------------------
    st.subheader("🔍 Breakdown by Sensor Type")

    rows = []
    for key, stats in agg.items():
        icon, label, unit = sensor_labels.get(key, ("📡", key.title(), ""))
        rows.append({
            "Sensor Type": f"{icon} {label}",
            "Unit": unit,
            "Average": stats["avg"],
            "Min": stats["min"],
            "Max": stats["max"],
            "Readings": stats["count"],
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(table_df, width="stretch", hide_index=True)

    st.divider()

    # -----------------------
    # Bar Chart
    # -----------------------
    st.subheader("📊 Average Measurements by Sensor Type")

    chart_data = {
        sensor_labels.get(k, ("📡", k.title(), ""))[1]: v["avg"]
        for k, v in agg.items()
    }

    chart_df = pd.DataFrame.from_dict(
        chart_data, orient="index", columns=["Average"]
    )

    st.bar_chart(chart_df)

else:
    st.info("Apply filters above and click **Fetch Data** to view aggregated statistics.")
