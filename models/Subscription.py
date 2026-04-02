from dataclasses import dataclass

@dataclass
class Subscription:
    subscription_id: str
    subscriber_id: str
    rule_id: str
    rule_name: str