from dataclasses import dataclass

from models import Coordinate, SensorType

@dataclass
class SensorData:
    sensor_id: str
    measurement: float
    unit: str
    time: int
    location: Coordinate
    sensor_type: SensorType
    country: str
    city: str