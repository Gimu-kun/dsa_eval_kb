
from MetaModel import Instance
from Ontology.DSA_Ontology.Concepts.bloom_levels import (
    BloomLevel_Remember,
    BloomLevel_Understand,
    BloomLevel_Apply
)

remember_instance = Instance(
    id="I_BLOOM_LEVEL_REMEMBER",
    concept_id=BloomLevel_Remember.id,
    attributes={
        "weight": 1,
        "name": "Remember"
    }
)

understand_instance = Instance(
    id="I_BLOOM_LEVEL_UNDERSTAND",
    concept_id=BloomLevel_Understand.id,
    attributes={
        "weight": 2,
        "name": "Understand"
    }
)

apply_instance = Instance(
    id="I_BLOOM_LEVEL_APPLY",
    concept_id=BloomLevel_Apply.id,
    attributes={
        "weight": 3,
        "name": "Apply"
    }
)

bloom_level_instances = [
    remember_instance,
    understand_instance,
    apply_instance
]
