from enum import Enum

class ComparisonOperator(Enum):
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"