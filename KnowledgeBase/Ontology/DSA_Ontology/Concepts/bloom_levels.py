from MetaModel.classes import Concept, Attribute
from MetaModel.classes.enums.types import Cardinality, ValueType


BloomLevel = Concept(
    id="O_C_BLOOM_LEVEL",
    name="BloomLevel",
    domain="DSA",
    subclassOf="",
    attributes=[
        Attribute(
            name="name",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

BloomLevel_Remember = Concept(
    id="O_C_BLOOM_LEVEL_REMEMBER",
    name="Remember",
    domain="DSA",
    subclassOf=BloomLevel.id,
    attributes=[
        Attribute(
            name="weight",
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
    domain="DSA",
    subclassOf=BloomLevel.id,
    attributes=[
        Attribute(
            name="weight",
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
    domain="DSA",
    subclassOf=BloomLevel.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)