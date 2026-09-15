from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .Attribute import AttributeDefinition
    from .Invariant import Invariant
    from .Operation import Operation

@dataclass
class Concept:
    id: str
    name: str
    domain: str
    subclass_of: Optional[str] = None
    attributes: list[AttributeDefinition] = field(default_factory=list)
    invariant: list[Invariant] = field(default_factory=list)
    operation: list[Operation] = field(default_factory=list)

    @property
    def subclassOf(self) -> Optional[str]:
        return self.subclass_of

    @subclassOf.setter
    def subclassOf(self, value: Optional[str]):
        self.subclass_of = value

    def display_name(self) -> str:
        for attr in self.attributes:
            if attr.name == "name" and attr.default not in (None, ""):
                return str(attr.default)
        return self.name or self.id
