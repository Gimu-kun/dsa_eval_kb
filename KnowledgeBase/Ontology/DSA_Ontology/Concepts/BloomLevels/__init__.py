from MetaModel.classes import Concept, Attribute
from MetaModel.classes.enums.types import Cardinality, ValueType


BloomLevel = Concept(
    id="O_C_BLOOM_LEVEL",
    name="BloomLevel",
    domain="BloomLevel",
    subclassOf="",
    attributes=[],
    invariant=[],
    operation=[]
)

BloomLevel_Remember = Concept(
    id="O_C_BLOOM_LEVEL_REMEMBER",
    name="Remember",
    domain="BloomLevel",
    subclassOf="O_C_BLOOM_LEVEL",
    attributes=[
        Attribute(
            name="level",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

BloomLevel_Understand = Concept(
    id="O_C_BLOOM_LEVEL_UNDERSTAND",
    name="Understand",
    domain="BloomLevel",
    subclassOf="O_C_BLOOM_LEVEL",
    attributes=[
        Attribute(
            name="level",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

BloomLevel_Apply = Concept(
    id="O_C_BLOOM_LEVEL_APPLY",
    name="Apply",
    domain="BloomLevel",
    subclassOf="O_C_BLOOM_LEVEL",
    attributes=[
        Attribute(
            name="level",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)