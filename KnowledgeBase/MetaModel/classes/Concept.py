from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .Attribute import Attribute
    from .Invariant import Invariant
    from .Operation import Operation


@dataclass
class Concept:
    id: str
    name: str
    domain: str
    subclassOf: str
    attributes: 'List[Attribute]' = field(default_factory=list)
    invariant: 'List[Invariant]' = field(default_factory=list)
    operation: 'List[Operation]' = field(default_factory=list)
