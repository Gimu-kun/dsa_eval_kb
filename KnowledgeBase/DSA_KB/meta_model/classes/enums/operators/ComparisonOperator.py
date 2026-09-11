from enum import Enum


class ComparisonOperator(Enum):
    EQ = "EQ"   #Equal
    NEQ = "NEQ" #Not Equal
    GT = "GT"   #Greater Than
    GTE = "GTE" #Greater Than Equal
    LT = "LT"   #Less Than
    LTE = "LTE" #Less Than Equal
    IN = "IN"
    RANGE = "RANGE"
    MIN = "MIN"
    MAX = "MAX"