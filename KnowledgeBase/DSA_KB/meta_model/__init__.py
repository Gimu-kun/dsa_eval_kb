from __future__ import annotations
from typing import Union, Optional
from dataclasses import dataclass, field

from .classes import (
    Instance, Assertion, Hierarchy, Concept, Relation, Rule,
    Operation, Function, Invariant, Parameter, Operand
)

PrimitiveType = Union[int, float, str, bool, None]
ReferenceType = Union[str, list[str], None]

@dataclass
class DataLayer:
    """Tầng dữ liệu cụ thể D = <I, A> gồm Instances và Assertions"""
    instances: list[Instance] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)

@dataclass
class Ontology:
    """Tầng mô hình bản thể học O = <C, H, Rel, Ru, F, Op, Opd>"""
    concepts: list[Concept] = field(default_factory=list)
    hierarchies: list[Hierarchy] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    operations: list[Operation] = field(default_factory=list)
    operands: list[Operand] = field(default_factory=list)

@dataclass
class KnowledgeBase:
    """Cấu trúc hệ tri thức tổng quát KB = <M, O, D> với D = <I, A>"""
    ontology: Ontology
    data: DataLayer = field(default_factory=DataLayer)

    def __init__(
        self,
        ontology: Ontology,
        data: Optional[DataLayer] = None,
        instances: Optional[list[Instance]] = None,
        assertions: Optional[list[Assertion]] = None,
    ):
        self.ontology = ontology
        if data is not None:
            self.data = data
        else:
            self.data = DataLayer(
                instances=instances if instances is not None else [],
                assertions=assertions if assertions is not None else [],
            )

    @property
    def instances(self) -> list[Instance]:
        return self.data.instances

    @instances.setter
    def instances(self, val: list[Instance]):
        self.data.instances = val

    @property
    def assertions(self) -> list[Assertion]:
        return self.data.assertions

    @assertions.setter
    def assertions(self, val: list[Assertion]):
        self.data.assertions = val