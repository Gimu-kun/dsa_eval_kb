from KnowledgeBase.DSA_KB.meta_model.classes.Attribute import AttributeValue
from dataclasses import dataclass, field


@dataclass
class Instance:
    id: str
    instanceOf: str
    attributes: list[AttributeValue] = field(default_factory=list)