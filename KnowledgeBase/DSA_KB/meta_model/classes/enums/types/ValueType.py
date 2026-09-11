from enum import Enum


class ValueType(Enum):
    INTEGER = "int"
    FLOAT = "float"
    STRING = "str"
    BOOLEAN = "bool"
    CONCEPT = "concept"
    PRIMITIVE = "primitive"
    REFERENCE = "reference"
    VARIABLE = "variable"
    FUNC = "func"
    CONDITION = "condition"
    RELATION = "relation"
    INSTANCE = "instance"
    ANY = "any"