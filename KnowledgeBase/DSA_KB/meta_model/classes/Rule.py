from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Union, Optional

from .Attribute import AttributeValue

if TYPE_CHECKING:
    from .Condition import Condition

class ConclusionType(Enum):
    ATTRIBUTE = "attribute" #Cập nhật dữ liệu
    ASSERTION = "assertion" #Kết luận quan hệ mới
    INSTANCE = "instance" #Kết luận khái niệm mới

@dataclass
class AttributeConclusion:
    type: ConclusionType = ConclusionType.ATTRIBUTE
    target_instance: str = ""
    attribute_name: str = ""
    valueType: str = ""
    value: Union[str, int, float, bool] = None

@dataclass
class RelationConclusion:
    type: ConclusionType = ConclusionType.ASSERTION
    source_instance: str = ""
    relation_id: str = ""
    target_instance: str = ""
    attributes: list[AttributeValue] = field(default_factory=list)

@dataclass
class ConceptConclusion:
    type: ConclusionType = ConclusionType.INSTANCE
    target_instance: str = ""
    attributes: list[AttributeValue] = field(default_factory=list)

ConclusionTypeAlias = Union[AttributeConclusion, RelationConclusion, ConceptConclusion]

@dataclass
class Rule:
    id: str
    name: str
    condition: Condition
    conclusion: list[ConclusionTypeAlias]
    description: Optional[str] = None
    expression: Optional[str] = None