from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from typing import Any

if TYPE_CHECKING:
    from .enums.types import ValueType
    from .Condition import Condition

@dataclass
class AttributeDefinition:
    name: str
    value_type: ValueType
    required: bool
    constraint: Optional[Condition] = None

@dataclass
class AttributeValue:
    name: str
    value: int|bool|str|float|None