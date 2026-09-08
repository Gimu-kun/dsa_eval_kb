from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .enums.types import Cardinality, ValueType
    from .Condition import Condition


@dataclass
class Relation:
    id: str
    name: str
    source: str
    cardinality: Cardinality
    value_type: ValueType
    value_domain: Optional[list[str]]
    constraint: Optional[Condition] = None