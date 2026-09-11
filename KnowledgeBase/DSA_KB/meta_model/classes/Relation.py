from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .enums.types import Cardinality, ValueType
    from .Condition import Condition
    from .Attribute import AttributeDefinition


@dataclass
class Relation:
    id: str
    name: str
    source: str
    cardinality: Cardinality
    target: str
    constraint: Optional[Condition] = None
    attributes: list[AttributeDefinition] = field(default_factory=list)