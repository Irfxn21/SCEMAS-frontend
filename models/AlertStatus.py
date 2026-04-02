from enum import Enum

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEGED = "acknowledged"
    RESOLVED = "resolved"