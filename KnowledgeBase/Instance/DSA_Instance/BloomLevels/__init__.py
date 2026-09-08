
from MetaModel import Instance
from Ontology.DSA_Ontology.Concepts.BloomLevels import (
    BloomLevel_Remember,
    BloomLevel_Understand,
    BloomLevel_Apply
)

remember_instance = Instance(
    id="I_BLOOM_LEVEL_REMEMBER_1",
    concept_id=BloomLevel_Remember.id,
    attributes={
        "level": 1,
        "name": "Remember"
    }
)

understand_instance = Instance(
    id="I_BLOOM_LEVEL_UNDERSTAND_1",
    concept_id=BloomLevel_Understand.id,
    attributes={
        "level": 2,
        "name": "Understand"
    }
)

apply_instance = Instance(
    id="I_BLOOM_LEVEL_APPLY_1",
    concept_id=BloomLevel_Apply.id,
    attributes={
        "level": 3,
        "name": "Apply"
    }
)

bloom_level_instances = [
    remember_instance,
    understand_instance,
    apply_instance
]
