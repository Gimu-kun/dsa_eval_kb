from typing import Union
from dataclasses import dataclass
from dataclasses import field

from MetaModel.classes import Concept, Relation, Rule, Operation

PrimitiveType = Union[int, float, str, bool, None]
ReferenceType = Union[str, list[str], None]

@dataclass
class Ontology:
    concepts:list[Concept] = field(default_factory=list)
    relations:list[Relation] = field(default_factory=list)
    rules:list[Rule] = field(default_factory=list)
    operations:list[Operation] = field(default_factory=list)

@dataclass
class Instance:
    id: str
    concept_id: str
    attributes: dict[str, PrimitiveType] = field(default_factory=dict)
    relations: dict[str, ReferenceType] = field(default_factory=dict)

@dataclass
class KnowledgeBase:
    ontology: Ontology
    instances: list[Instance] = field(default_factory=list)