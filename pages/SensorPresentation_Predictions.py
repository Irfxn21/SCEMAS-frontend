import streamlit as st
import pandas as pd

from clients.SensorClient import predict_data
from models.SensorType import SensorType
from utils.Initialize import initialize
from utils.Sidebar import render_sidebar


# -----------------------
# Page Setup
# -----------------------
st.set_page_config(layout="wide")

st.session_state.page = "predictions"

initialize()
render_sidebar()

st.title('🧠 Predictions')
st.caption('Forecast sensor measurements for the next 30 days')

# -----------------------
# Filters
# -----------------------
st.subheader("Filters")

input_cols = st.columns(3)

country = input_cols[0].text_input("Country")
city = input_cols[1].text_input("City")

sensor_type = input_cols[2].selectbox(
    "Sensor Type",
    options=list(SensorType),
    format_func=lambda x: x.value
)

submit = st.button("Submit", width='stretch')


# -----------------------
# Handle Submit
# -----------------------
if submit:
    if not country or not city or not sensor_type:
        st.divider()
        st.warning("Please fill in all fields before submitting.")
        st.stop()

    st.session_state.predictions_submitted = True

    try:
        predictions = predict_data(
            country=country,
            city=city,
            sensor_type=sensor_type
        )
    except Exception:
        st.error("Failed to fetch prediction data.")
        st.stop()

    st.session_state.predictions = predictions


# -----------------------
# Divider
# -----------------------
st.divider()


# -----------------------
# Pre-submit State
# -----------------------
if not st.session_state.predictions_submitted:
    st.info("Enter filters above and click Submit to view predictions.")
    st.stop()


# -----------------------
# Results
# -----------------------
predictions = st.session_state.predictions

if not predictions:
    st.info("No prediction data available.")
    st.stop()


# -----------------------
# Convert to DataFrame
# -----------------------
df = pd.DataFrame([p.__dict__ for p in predictions])

# Convert timestamp
df["time"] = pd.to_datetime(df["time"], unit="s")

df = df.sort_values("time")


# -----------------------
# Line Chart
# -----------------------
st.subheader("Prediction Trend (Next 30 Days)")

chart_df = df[["time", "measurement"]].set_index("time")

st.line_chart(chart_df, width='stretch')


# -----------------------
# Raw Data (Expandable)
# -----------------------
with st.expander("🔍 View Raw Data"):
    display_df = df[
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

    st.dataframe(display_df, width="stretch")