from enum import Enum


class ValueType(Enum):
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    CONCEPT = "concept"
    PRIMITIVE = "primitive"
    REFERENCE = "reference"
    VARIABLE = "variable"
    FUNC = "func"
    CONDITION = "condition"
    ANY = "any"