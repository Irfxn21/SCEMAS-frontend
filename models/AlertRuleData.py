from dataclasses import dataclass
from models import ComparisonOperator, Coordinate, SensorType

@dataclass
class AlertRuleData:
    rule_id: str
    author_id: str
    name: str
    threshold: float
    operator: ComparisonOperator
    location: Coordinate
    radius: float
    sensor_type: SensorType
    created_at: int
    updated_at: int

    def evaluate(self, value: float) -> bool:
        if self.operator == ComparisonOperator.GREATER_THAN:
            return value > self.threshold
        elif self.operator == ComparisonOperator.LESS_THAN:
            return value < self.threshold
        elif self.operator == ComparisonOperator.GREATER_OR_EQUAL:
            return value >= self.threshold
        elif self.operator == ComparisonOperator.LESS_OR_EQUAL:
            return value <= self.threshold
        elif self.operator == ComparisonOperator.EQUAL:
            return value == self.threshold
        elif self.operator == ComparisonOperator.NOT_EQUAL:
            return value != self.threshold
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")