from enum import Enum


class ConditionType(Enum):
    LOGICAL = "Logical"
    COMPARISON = "Comparison"
    DOMAIN = "Domain"
    EXISTENCE = "Existence"
    RELATION = "Relation"