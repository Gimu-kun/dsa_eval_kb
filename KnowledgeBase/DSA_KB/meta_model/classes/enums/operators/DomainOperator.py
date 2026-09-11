from enum import Enum


class DomainOperator(Enum):
    ENUM = "ENUM"
    IN = "IN"
    RANGE = "RANGE"
    NOT_IN = "NOT_IN"
    BETWEEN = "BETWEEN"