import streamlit as st
from typing import List, Dict, Optional
import time
import random

from utils.Request import request

from models.SensorData import SensorData
from models.SensorType import SensorType
from models.Coordinate import Coordinate

base_url = st.secrets["BACKEND_BASE_URL"]

USE_MOCKS = True

# ----------------------
# Stable randomness (per session)
# ----------------------
if "sensor_seed" not in st.session_state:
    st.session_state.sensor_seed = random.randint(0, 100000)

random.seed(st.session_state.sensor_seed)

# ----------------------
# Random pools
# ----------------------

CITIES = [
    ("Toronto", 43.6532, -79.3832),
    ("Mississauga", 43.5890, -79.6441),
    ("Brampton", 43.7315, -79.7624),
    ("Oakville", 43.4675, -79.6877),
    ("Hamilton", 43.2557, -79.8711),
    ("Burlington", 43.3255, -79.7990),
    ("Milton", 43.5183, -79.8774),
]

UNITS = {
    SensorType.TEMPERATURE: "°C",
    SensorType.HUMIDITY: "%",
    SensorType.NOISE: "dB",
    SensorType.AIR_QUALITY: "AQI",
}

# ----------------------
# Mock Generators
# ----------------------

def _mock_sensor(sensor_id: str = None) -> SensorData:
    city, lat, lon = random.choice(CITIES)
    sensor_type = random.choice(list(SensorType))

    return SensorData(
        sensor_id=sensor_id or f"sensor-{random.randint(100,999)}",
        measurement=round(random.uniform(10, 100), 2),
        unit=UNITS[sensor_type],
        time=int(time.time()) - random.randint(0, 3600),
        location=Coordinate(
            latitude=lat + random.uniform(-0.05, 0.05),
            longitude=lon + random.uniform(-0.05, 0.05),
        ),
        sensor_type=sensor_type,
        country="Canada",
        city=city
    )


def _mock_aggregated() -> Dict[str, dict]:
    result = {}

    for sensor_type in SensorType:
        values = [random.uniform(10, 100) for _ in range(random.randint(5, 20))]
        result[sensor_type.value] = {
            "avg": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "count": len(values)
        }

    return result


# ----------------------
# Parsers
# ----------------------

def _parse_sensor(data: dict) -> SensorData:
    return SensorData(
        sensor_id=data["sensor_id"],
        measurement=data["measurement"],
        unit=data["unit"],
        time=data["time"],
        location=Coordinate(
            latitude=data["location"]["latitude"],
            longitude=data["location"]["longitude"]
        ),
        sensor_type=SensorType(data["sensor_type"]),
        country=data["country"],
        city=data["city"]
    )


def _unwrap(response):
    if not response["success"]:
        raise Exception(response["error"])
    return response["data"]


# ----------------------
# Sensors
# ----------------------

def get_sensor_data() -> List[SensorData]:
    if USE_MOCKS:
        return [_mock_sensor() for _ in range(30)]
    else:
        res = request("GET", f"{base_url}/sensors/")
        return [_parse_sensor(s) for s in _unwrap(res)]


def get_sensor_data_by_id(sensor_id: str) -> SensorData:
    if USE_MOCKS:
        return _mock_sensor(sensor_id)
    else:
        res = request("GET", f"{base_url}/sensors/{sensor_id}")
        return _parse_sensor(_unwrap(res))


def get_aggregated_data(
    country: Optional[str] = None,
    city: Optional[str] = None,
    sensor_type: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> Dict[str, dict]:

    params = {
        "country": country,
        "city": city,
        "sensor_type": sensor_type,
        "start_time": start_time,
        "end_time": end_time
    }

    # remove None values
    params = {k: v for k, v in params.items() if v is not None}

    if USE_MOCKS:
        return _mock_aggregated()
    else:
        res = request("GET", f"{base_url}/sensors/aggregated", params=params)
        return _unwrap(res)


def get_filtered_sensor_data(
    country: Optional[str] = None,
    city: Optional[str] = None,
    sensor_type: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> List[SensorData]:

    params = {
        "country": country,
        "city": city,
        "sensor_type": sensor_type,
        "start_time": start_time,
        "end_time": end_time
    }

    # remove None values
    params = {k: v for k, v in params.items() if v is not None}

    if USE_MOCKS:
        return [_mock_sensor() for _ in range(random.randint(5, 20))]
    else:
        res = request("GET", f"{base_url}/sensors/filter", params=params)
        return [_parse_sensor(s) for s in _unwrap(res)]