import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, Fullscreen, MarkerCluster

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

    # -----------------------
    # Fetch Data (safe)
    # -----------------------
    sensors = []
    fetch_failed = False

    if st.session_state.get("sensor_data") is None:
        try:
            st.session_state["sensor_data"] = get_sensor_data()
        except Exception:
            fetch_failed = True
            st.session_state["sensor_data"] = []

    sensors = st.session_state["sensor_data"]

    # -----------------------
    # Base Map (ALWAYS CREATE)
    # -----------------------
    m = folium.Map(
        location=[20, 0],  # default world view
        zoom_start=2,
        tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        attr='© HOT'
    )

    m.options['maxBounds'] = [[-85, -180], [85, 180]]
    m.options['maxBoundsViscosity'] = 1.0
    m.options['minZoom'] = 2

    # -----------------------
    # Sensor Type Colors
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

    # -----------------------
    # Process Data (only if exists)
    # -----------------------
    filtered_df = pd.DataFrame()

    if not fetch_failed and sensors:
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
            # Deduplicate latest per location
            filtered_df = filtered_df.sort_values("time", ascending=False)
            filtered_df = filtered_df.drop_duplicates(
                subset=["latitude", "longitude"],
                keep="first"
            )

            # Fit bounds
            bounds = [
                [filtered_df["latitude"].min(), filtered_df["longitude"].min()],
                [filtered_df["latitude"].max(), filtered_df["longitude"].max()]
            ]
            m.fit_bounds(bounds)

            # Add markers
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
    # Messages (NO st.stop)
    # -----------------------
    if fetch_failed:
        st.error("Failed to fetch sensor data. Showing empty map.")

    elif not sensors:
        st.info("No sensor data available. Showing empty map.")

    elif filtered_df.empty:
        st.warning("No sensor data matches the selected filters.")

    # -----------------------
    # Legend (always visible)
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
    # Render Map (ALWAYS)
    # -----------------------
    st_folium(m, use_container_width=True)


# -----------------------
# Graphs Tab
# -----------------------
with graphs_tab:
    st.info("Graphs coming soon...")