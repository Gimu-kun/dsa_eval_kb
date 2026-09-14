from enum import Enum


class Cardinality(Enum):
    ONE_ONE = "(1..1)"
    ZERO_ONE = "(0..1)"
    ONE_MANY = "(1..*)"
    ZERO_MANY = "(0..*)"
    MANY_MANY = "(*..*)"