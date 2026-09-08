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

    def __post_init__(self):
        # Create a lookup for concepts
        concept_map = {concept.id: concept for concept in self.ontology.concepts}

        # Function to get all expected attributes for a concept (including inherited)
        def get_expected_attributes(concept_id):
            attrs = set()
            current_id = concept_id
            while current_id:
                concept = concept_map.get(current_id)
                if not concept:
                    break
                for attr in concept.attributes:
                    attrs.add(attr.name)
                current_id = concept.subclassOf
            return attrs

        # Validate instances
        for instance in self.instances:
            if instance.concept_id not in concept_map:
                raise ValueError(f"Instance '{instance.id}' references unknown concept '{instance.concept_id}'")
            
            expected_attrs = get_expected_attributes(instance.concept_id)
            actual_attrs = set(instance.attributes.keys())
            
            # Check if all expected attributes are provided
            missing_attrs = expected_attrs - actual_attrs
            if missing_attrs:
                raise ValueError(f"Instance '{instance.id}' (Concept '{instance.concept_id}') is missing required attributes: {missing_attrs}")
                
            # Check if there are unexpected attributes provided
            unexpected_attrs = actual_attrs - expected_attrs
            if unexpected_attrs:
                raise ValueError(f"Instance '{instance.id}' (Concept '{instance.concept_id}') has unexpected attributes: {unexpected_attrs}")