from dataclasses import dataclass, field
from .Attribute import AttributeValue

@dataclass
class Assertion:
    source: str
    relation: str
    target: str
    attributes: list[AttributeValue] = field(default_factory=list)
