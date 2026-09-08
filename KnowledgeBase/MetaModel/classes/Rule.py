from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Condition import Condition

@dataclass
class Rule:
    id: str
    name: str
    condition: Condition
    conclusion: Condition