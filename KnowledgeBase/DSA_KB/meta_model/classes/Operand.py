from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enums.types import ValueType

@dataclass
class Operand:
    operand_type: ValueType
    value: str