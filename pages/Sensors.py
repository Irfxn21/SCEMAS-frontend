import streamlit as st
import pandas as pd

from clients.SensorClient import get_sensor_data
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")

st.session_state.page = "sensors"

initialize()
render_sidebar()

st.title('📡 Sensors')
st.caption('View sensor data.')

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

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
# Fetch data
# -----------------------
st.divider()
st.subheader("Results")

if st.session_state.get("sensors_data") is None:
    try:
        st.session_state["sensors_data"] = get_sensor_data()
    except:
        st.error("Failed to fetch sensor data.")
        st.stop()

sensors = st.session_state["sensors_data"]

if not sensors:
    st.info("No sensor data available.")
    st.stop()

df = pd.DataFrame([s.__dict__ for s in sensors])

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
    st.warning("No sensor data match the selected filters.")
else:
    display_df = filtered_df[
        [
            "sensor_id",
            "sensor_type",
            "measurement",
            "unit",
            "time",
            "country",
            "city",
            "location"
        ]
    ].copy()

    display_df["sensor_type"] = display_df["sensor_type"].apply(lambda x: x.value)

    def format_location(loc):
        if pd.isna(loc):
            return None
        try:
            return f"{loc.latitude}, {loc.longitude}"
        except AttributeError:
            return str(loc)

    display_df["location"] = display_df["location"].apply(format_location)

    event = st.dataframe(
        display_df,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
    )

    prev_selected = st.session_state.get("sensors_selected")

    if event.selection["rows"]:
        selected_index = event.selection["rows"][0]
        new_selected = filtered_df.iloc[selected_index]

        if prev_selected is None or prev_selected.sensor_id != new_selected.sensor_id:
            st.session_state["sensors_show_dialog"] = False

        st.session_state["sensors_selected"] = new_selected
    else:
        st.session_state["sensors_selected"] = None
        st.session_state["sensors_show_dialog"] = False

    if st.session_state["sensors_selected"] is not None:
        st.success(
            f"Selected: {st.session_state['sensors_selected']['sensor_id']}"
        )

        if st.button("View Details"):
            st.session_state["sensors_show_dialog"] = True


# -----------------------
# Dialog
# -----------------------
if st.session_state.get("sensors_show_dialog", False):

    sensor = st.session_state.get("sensors_selected")

    @st.dialog("Sensor Details", width="medium")
    def show_sensor_dialog():
        if sensor is not None:
            sensor_dict = sensor.to_dict()

            sensor_dict["sensor_type"] = sensor_dict["sensor_type"].value
            sensor_dict["location"] = {
                "longitude": sensor_dict["location"].longitude,
                "latitude": sensor_dict["location"].latitude,
            }

            st.json(sensor_dict)

    show_sensor_dialog()