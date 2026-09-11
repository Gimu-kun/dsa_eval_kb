from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Condition import Condition

@dataclass
class Invariant:
    name: str
    condition: Condition
    description: Optional[str] = None