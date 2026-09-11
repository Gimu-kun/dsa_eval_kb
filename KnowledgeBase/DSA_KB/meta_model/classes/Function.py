from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .Attribute import Attribute

@dataclass
class Function:
    id: str
    name: str
    input: list[Attribute] = field(default_factory=list)
    output: Optional[Attribute] = None