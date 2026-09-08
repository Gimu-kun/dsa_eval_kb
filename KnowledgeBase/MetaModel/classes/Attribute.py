from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .enums.types import ValueType, Cardinality
    from .Condition import Condition

@dataclass
class Attribute:
    name: str
    value_type: ValueType
    value_domain: Optional[list[str]]
    cardinality: Cardinality
    constraint: Optional[Condition] = None