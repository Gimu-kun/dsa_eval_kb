from __future__ import annotations
from dataclasses import dataclass

from .enums.types import Cardinality

PRIMITIVE_VALUE_TYPES = {
    "int",
    "float",
    "str",
    "bool",
    "any",
    "string",
    "integer",
    "boolean",
}


@dataclass
class Parameter:
    name: str
    value_type: str
    required: bool = True
    cardinality: Cardinality = Cardinality.ONE_ONE

    @property
    def valueType(self) -> str:
        return self.value_type

    @valueType.setter
    def valueType(self, val: str):
        self.value_type = val

    @property
    def is_primitive(self) -> bool:
        return (self.value_type or "").lower() in PRIMITIVE_VALUE_TYPES

    @property
    def is_concept_ref(self) -> bool:
        return not self.is_primitive and bool(self.value_type)
