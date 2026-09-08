from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Attribute import Attribute


@dataclass
class Operation:
    name: str
    input: list[Attribute] = field(default_factory=list)
    output: list[Attribute] = field(default_factory=list)