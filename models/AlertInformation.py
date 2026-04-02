from dataclasses import dataclass

from models import AlertSeverity, AlertStatus
from models.SensorType import SensorType

@dataclass
class AlertInformation:
    alert_id: str
    rule_id: str
    sensor_id: str
    rule_name: str
    time: int
    sensor_type: SensorType
    severity: AlertSeverity
    status: AlertStatus
    country: str
    city: str