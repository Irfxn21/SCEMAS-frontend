import streamlit as st
from typing import List
import time
import uuid

from utils.Request import request

from models.AlertInformation import AlertInformation
from models.AlertRuleData import AlertRuleData
from models.Subscription import Subscription
from models.Coordinate import Coordinate

from models.AlertSeverity import AlertSeverity
from models.AlertStatus import AlertStatus
from models.SensorType import SensorType
from models.ComparisonOperator import ComparisonOperator

base_url = st.secrets["BACKEND_BASE_URL"]

USE_MOCKS = True


# ----------------------
# Mock Generators
# ----------------------

def _mock_alert(alert_id: str = None) -> AlertInformation:
    return AlertInformation(
        alert_id=alert_id or str(uuid.uuid4()),
        rule_id="rule-123",
        sensor_id="sensor-456",
        rule_name="High Temperature",
        time=int(time.time()),
        sensor_type=SensorType.TEMPERATURE,
        severity=AlertSeverity.HIGH,
        status=AlertStatus.ACTIVE,
        country="Canada",
        city="Hamilton"
    )


def _mock_rule(rule_id: str = None) -> AlertRuleData:
    return AlertRuleData(
        rule_id=rule_id or str(uuid.uuid4()),
        author_id="user-1",
        name="Temperature Threshold",
        threshold=30.0,
        operator=ComparisonOperator.GREATER_THAN,
        location=Coordinate(latitude=43.2557, longitude=-79.8711),
        radius=10.0,
        sensor_type=SensorType.TEMPERATURE,
        created_at=int(time.time()),
        updated_at=int(time.time())
    )


def _mock_subscription(rule_id: str = None) -> Subscription:
    return Subscription(
        subscription_id=str(uuid.uuid4()),
        subscriber_id="user-1",
        rule_id=rule_id or "rule-123",
        rule_name="Temperature Threshold"
    )

# ----------------------
# Helpers (parsers)
# ----------------------

def _parse_alert(data: dict) -> AlertInformation:
    return AlertInformation(
        alert_id=data["alert_id"],
        rule_id=data["rule_id"],
        sensor_id=data["sensor_id"],
        rule_name=data["rule_name"],
        time=data["time"],
        sensor_type=SensorType(data["sensor_type"]),
        severity=AlertSeverity(data["severity"]),
        status=AlertStatus(data["status"]),
        country=data["country"],
        city=data["city"]
    )


def _parse_alert_rule(data: dict) -> AlertRuleData:
    return AlertRuleData(
        rule_id=data["rule_id"],
        author_id=data["author_id"],
        name=data["name"],
        threshold=data["threshold"],
        operator=ComparisonOperator(data["operator"]),
        location=Coordinate(
            latitude=data["location"]["latitude"],
            longitude=data["location"]["longitude"]
        ),
        radius=data["radius"],
        sensor_type=SensorType(data["sensor_type"]),
        created_at=data["created_at"],
        updated_at=data["updated_at"]
    )


def _parse_subscription(data: dict) -> Subscription:
    return Subscription(
        subscription_id=data["subscription_id"],
        subscriber_id=data["subscriber_id"],
        rule_id=data["rule_id"],
        rule_name=data["rule_name"]
    )


def _unwrap(response):
    if not response["success"]:
        raise Exception(response["error"])
    return response["data"]


# ----------------------
# Alerts
# ----------------------

def get_alerts() -> List[AlertInformation]:
    if USE_MOCKS:
        return [_mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert(), _mock_alert()]
    else: 
        res = request("GET", f"{base_url}/alerts/")
        return [_parse_alert(a) for a in _unwrap(res)]


def get_alert(alert_id: str) -> AlertInformation:
    if USE_MOCKS:
        return _mock_alert(alert_id)
    else:
        res = request("GET", f"{base_url}/alerts/{alert_id}")
        return _parse_alert(_unwrap(res))


def update_alert(alert_id: str, alert_status: str, alert_severity: str) -> bool:
    res = request(
        "PUT",
        f"{base_url}/alerts/update",
        params={
            "alert_id": alert_id,
            "alert_status": alert_status,
            "alert_severity": alert_severity
        }
    )
    _unwrap(res)
    return True


# ----------------------
# Alert Rules
# ----------------------

def create_alert_rule(
    name: str,
    threshold: float,
    operator: str,
    latitude: float,
    longitude: float,
    radius: float,
    sensor_type: str
) -> AlertRuleData:

    res = request(
        "POST",
        f"{base_url}/alerts/rules/create",
        params={
            "name": name,
            "threshold": threshold,
            "operator": operator,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "sensor_type": sensor_type
        }
    )

    return _parse_alert_rule(_unwrap(res))


def delete_alert_rule(rule_id: str) -> bool:
    res = request("DELETE", f"{base_url}/alerts/rules/delete/{rule_id}")
    _unwrap(res)
    return True


def get_all_alert_rules() -> List[AlertRuleData]:
    if USE_MOCKS:
        return [_mock_rule(), _mock_rule()]
    else:
        res = request("GET", f"{base_url}/alerts/rules")
        return [_parse_alert_rule(r) for r in _unwrap(res)]


def get_alert_rule(rule_id: str) -> AlertRuleData:
    if USE_MOCKS:
        return _mock_rule(rule_id)
    else:
        res = request("GET", f"{base_url}/alerts/rules/{rule_id}")
        return _parse_alert_rule(_unwrap(res))


# ----------------------
# Subscriptions
# ----------------------

def subscribe_to_alert(rule_id: str) -> bool:
    res = request("POST", f"{base_url}/alerts/subscribe/{rule_id}")
    _unwrap(res)
    return True


def unsubscribe_from_alert(rule_id: str) -> bool:
    res = request("DELETE", f"{base_url}/alerts/unsubscribe/{rule_id}")
    _unwrap(res)
    return True


def get_my_subscriptions() -> List[Subscription]:
    if USE_MOCKS:
        return [_mock_subscription(), _mock_subscription()]
    else:
        res = request("GET", f"{base_url}/alerts/subscriptions")
        return [_parse_subscription(s) for s in _unwrap(res)]