from KnowledgeBase.DSA_KB.meta_model.classes.Instance import Instance
from KnowledgeBase.DSA_KB.meta_model.classes.Assertion import Assertion
from KnowledgeBase.DSA_KB.meta_model.classes.Hierarchy import Hierarchy
from typing import Union
from dataclasses import dataclass, field

from .classes import Concept, Relation, Rule, Operation

PrimitiveType = Union[int, float, str, bool, None]
ReferenceType = Union[str, list[str], None]

@dataclass
class Ontology:
    concepts: list[Concept] = field(default_factory=list)
    hierarchies: list[Hierarchy] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    operations: list[Operation] = field(default_factory=list)


@dataclass
class KnowledgeBase:
    ontology: Ontology
    instances: list[Instance] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)