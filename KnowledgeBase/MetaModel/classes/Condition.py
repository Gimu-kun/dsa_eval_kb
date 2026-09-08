from dataclasses import dataclass, field
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Operand import Operand
    from .enums.types import ConditionType


@dataclass
class Condition:
    condition_type: ConditionType
    operator: str #Sử dụng toán tử Comparison|Domain|Existence|Logical
    operands: list[Condition|Operand] = field(default_factory=list)