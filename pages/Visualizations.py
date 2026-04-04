import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen

from clients.SensorClient import get_sensor_data
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar

# -----------------------
# Page setup
# -----------------------
st.set_page_config(layout="wide")
st.session_state.page = "visualizations"

initialize()
render_sidebar()

st.title('🗺️ Visualizations')
st.caption('View visualizations of sensor data')

map_tab, graphs_tab = st.tabs(["📍 Map", "📈 Graphs"])

# -----------------------
# Fetch Function
# -----------------------
def fetch_data():
    try:
        data = get_sensor_data()
        st.session_state["sensor_data"] = data
        st.session_state["fetch_failed"] = False
    except Exception:
        st.session_state["fetch_failed"] = True

if st.session_state["sensor_data"] is None and not st.session_state["fetch_failed"]:
    fetch_data()

# -----------------------
# Map Tab
# -----------------------
with map_tab:
    filterCols = st.columns(5)

    start_time = filterCols[0].datetime_input("Start", value=None)
    end_time = filterCols[1].datetime_input("End", value=None)
    country = filterCols[2].text_input("Country")
    city = filterCols[3].text_input("City")

    sensor_type = filterCols[4].selectbox(
        "Sensor",
        options=[None] + list(SensorType),
        format_func=lambda x: x.value if x else "All"
    )

    sensors = st.session_state["sensor_data"]
    fetch_failed = st.session_state["fetch_failed"]

    # -----------------------
    # Base Map (ALWAYS CREATE)
    # -----------------------
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        attr='© HOT'
    )

    m.options['maxBounds'] = [[-85, -180], [85, 180]]
    m.options['maxBoundsViscosity'] = 1.0
    m.options['minZoom'] = 2

    # -----------------------
    # Sensor Type Styles
    # -----------------------
    SENSOR_COLORS = {
        SensorType.AIR_QUALITY: "red",
        SensorType.NOISE: "blue",
        SensorType.TEMPERATURE: "orange",
        SensorType.HUMIDITY: "green",
    }

    SENSOR_ICONS = {
        SensorType.AIR_QUALITY: "wind",
        SensorType.NOISE: "volume-up",
        SensorType.TEMPERATURE: "thermometer-half",
        SensorType.HUMIDITY: "tint",
    }

    filtered_df = pd.DataFrame()

    # -----------------------
    # Process Data
    # -----------------------
    if sensors:
        df = pd.DataFrame([s.__dict__ for s in sensors])

        df["latitude"] = df["location"].apply(lambda x: x.latitude)
        df["longitude"] = df["location"].apply(lambda x: x.longitude)
        df["time"] = pd.to_datetime(df["time"], unit="s")

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

        if country:
            filtered_df = filtered_df[
                filtered_df["country"].str.contains(country, case=False, na=False)
            ]

        if city:
            filtered_df = filtered_df[
                filtered_df["city"].str.contains(city, case=False, na=False)
            ]

        if not filtered_df.empty:
            filtered_df = filtered_df.sort_values("time", ascending=False)
            filtered_df = filtered_df.drop_duplicates(
                subset=["latitude", "longitude"],
                keep="first"
            )

            bounds = [
                [filtered_df["latitude"].min(), filtered_df["longitude"].min()],
                [filtered_df["latitude"].max(), filtered_df["longitude"].max()]
            ]
            m.fit_bounds(bounds)

            for _, row in filtered_df.iterrows():
                sensor_type_val = row["sensor_type"]

                color = SENSOR_COLORS.get(sensor_type_val, "gray")
                icon_name = SENSOR_ICONS.get(sensor_type_val, "info-sign")

                popup_html = f"""
                <b>Sensor Type:</b> {sensor_type_val.value}<br>
                <b>Measurement:</b> {row['measurement']} {row['unit']}<br>
                <b>Date:</b> {row['time']}
                """

                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{sensor_type_val.value}: {row['measurement']} {row['unit']}",
                    icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
                ).add_to(m)

    # -----------------------
    # Messages
    # -----------------------
    if fetch_failed:
        st.error("Failed to fetch sensor data.")

    elif sensors is None:
        st.info("Loading sensor data...")

    elif not sensors:
        st.info("No sensor data available.")

    elif filtered_df.empty:
        st.warning("No sensor data matches the selected filters.")

    # -----------------------
    # Legend
    # -----------------------
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 150px;
        z-index: 9999;
        font-size: 14px;
        background-color: white;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        color: black;
    ">
    <b>Sensor Types</b><br><br>

    <i class="fa fa-wind" style="color:red"></i> Air Quality<br>
    <i class="fa fa-volume-up" style="color:blue"></i> Noise<br>
    <i class="fa fa-thermometer-half" style="color:orange"></i> Temperature<br>
    <i class="fa fa-tint" style="color:green"></i> Humidity
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # -----------------------
    # Controls
    # -----------------------
    LocateControl(auto_start=False, flyTo=True).add_to(m)
    Fullscreen().add_to(m)

    # -----------------------
    # Render Map
    # -----------------------
    st_folium(m, width='stretch')

# -----------------------
# Graphs Tab
# -----------------------
with graphs_tab:
    sensors = st.session_state["sensor_data"]
    fetch_failed = st.session_state["fetch_failed"]

    if fetch_failed:
        st.error("Failed to fetch sensor data.")

    elif sensors is None:
        st.info("Loading sensor data...")

    elif not sensors:
        st.info("No sensor data available.")

    else:
        df = pd.DataFrame([s.__dict__ for s in sensors])

        df["sensor_type"] = df["sensor_type"].apply(lambda x: x.value)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["latitude"] = df["location"].apply(lambda x: x.latitude)
        df["longitude"] = df["location"].apply(lambda x: x.longitude)
        df = df.drop(columns=["location"])

        # -----------------------
        # Filters
        # -----------------------
        filterCols = st.columns(5)

        start_time = filterCols[0].datetime_input("Start", value=None, key="g_start")
        end_time = filterCols[1].datetime_input("End", value=None, key="g_end")
        country = filterCols[2].text_input("Country", key="g_country")
        city = filterCols[3].text_input("City", key="g_city")

        sensor_options = ["All"] + sorted(df["sensor_type"].unique())

        sensor_type = filterCols[4].selectbox(
            "Sensor",
            options=sensor_options,
            key="g_sensor"
        )

        filtered_df = df.copy()

        if start_time:
            filtered_df = filtered_df[
                filtered_df["time"] >= pd.to_datetime(start_time)
            ]

        if end_time:
            filtered_df = filtered_df[
                filtered_df["time"] <= pd.to_datetime(end_time)
            ]

        if sensor_type != "All":
            filtered_df = filtered_df[
                filtered_df["sensor_type"] == sensor_type
            ]

        if country:
            filtered_df = filtered_df[
                filtered_df["country"].str.contains(country, case=False, na=False)
            ]

        if city:
            filtered_df = filtered_df[
                filtered_df["city"].str.contains(city, case=False, na=False)
            ]

        if filtered_df.empty:
            st.warning("No data matches the selected filters.")
            st.stop()

        # -----------------------
        # Graph Selector
        # -----------------------
        chart_type = st.selectbox(
            "Select Graph Type",
            ["Time Series", "Average by Sensor Type", "Distribution", "Count Over Time"]
        )

        # -----------------------
        # Time Series
        # -----------------------
        if chart_type == "Time Series":
            ts_df = filtered_df.sort_values("time")

            pivot_df = ts_df.pivot_table(
                index="time",
                columns="sensor_type",
                values="measurement",
                aggfunc="mean"
            )

            pivot_df = pivot_df.interpolate(method="time")

            st.line_chart(pivot_df)

        # -----------------------
        # Average
        # -----------------------
        elif chart_type == "Average by Sensor Type":
            avg_df = (
                filtered_df
                .groupby("sensor_type")["measurement"]
                .mean()
            )

            st.bar_chart(avg_df)

        # -----------------------
        # Distribution
        # -----------------------
        elif chart_type == "Distribution":
            selected_sensor = st.selectbox(
                "Select Sensor Type",
                filtered_df["sensor_type"].unique()
            )

            dist_df = filtered_df[
                filtered_df["sensor_type"] == selected_sensor
            ].copy()

            values = dist_df["measurement"].dropna()

            if values.empty:
                st.warning("No measurement data available for this sensor.")
                st.stop()

            # -----------------------
            # Bucket Strategy
            # -----------------------
            use_custom_bins = st.checkbox("Use meaningful ranges", value=True)

            def get_bins(sensor_type, values):
                if sensor_type == "Temperature":
                    return [-30, 0, 10, 20, 30, 40, 50]
                elif sensor_type == "Humidity":
                    return [0, 20, 40, 60, 80, 100]
                elif sensor_type == "Noise":
                    return [0, 30, 60, 80, 100, 120]
                elif sensor_type == "Air Quality":
                    return [0, 50, 100, 150, 200, 300, 500]
                else:
                    return np.linspace(values.min(), values.max(), 10)

            if use_custom_bins:
                bins = get_bins(selected_sensor, values)
            else:
                num_bins = st.slider("Number of Buckets", 5, 50, 15)
                bins = np.linspace(values.min(), values.max(), num_bins + 1)

            # -----------------------
            # Apply Bucketing
            # -----------------------
            dist_df["bucket"] = pd.cut(values, bins=bins, include_lowest=True, duplicates="drop")

            bucket_counts = (
                dist_df["bucket"]
                .value_counts()
                .sort_index()
            )

            # Make labels readable
            bucket_counts.index = bucket_counts.index.astype(str)

            # Optional normalization
            show_percentage = st.checkbox("Show as percentage", value=False)
            if show_percentage:
                bucket_counts = bucket_counts / bucket_counts.sum()

            # -----------------------
            # Chart
            # -----------------------
            st.bar_chart(bucket_counts)

            # -----------------------
            # Summary Stats
            # -----------------------
            col1, col2, col3 = st.columns(3)
            col1.metric("Min", round(values.min(), 2))
            col2.metric("Mean", round(values.mean(), 2))
            col3.metric("Max", round(values.max(), 2))

        # -----------------------
        # Count Over Time
        # -----------------------
        elif chart_type == "Count Over Time":
            freq = st.selectbox(
                "Aggregation Level",
                ["Hourly", "Daily", "Weekly"]
            )

            freq_map = {
                "Hourly": "h",
                "Daily": "D",
                "Weekly": "W"
            }

            count_df = (
                filtered_df
                .set_index("time")
                .groupby("sensor_type")
                .resample(freq_map[freq])
                .size()
                .unstack(level=0)
                .fillna(0)
            )

            st.line_chart(count_df)

        # -----------------------
        # Raw Data
        # -----------------------
        with st.expander("🔍 View Raw Data"):
            st.dataframe(filtered_df, width='stretch')