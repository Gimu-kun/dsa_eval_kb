from MetaModel.classes import Concept, Attribute
from MetaModel.classes.enums.types import Cardinality, ValueType

CLO = Concept(
    id="O_C_CLO",
    name="CLO",
    domain="DSA",
    subclassOf="",
    attributes=[],
    invariant=[],
    operation=[]
)

CLO1 = Concept(
    id="O_C_CLO_1",
    name="CLO1",
    domain="DSA",
    subclassOf=CLO.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ),
        Attribute(
            name="description",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

CLO2 = Concept(
    id="O_C_CLO_2",
    name="CLO2",
    domain="DSA",
    subclassOf=CLO.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ),
        Attribute(
            name="description",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

CLO3 = Concept(
    id="O_C_CLO_3",
    name="CLO3",
    domain="DSA",
    subclassOf=CLO.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ),
        Attribute(
            name="description",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)

CLO4 = Concept(
    id="O_C_CLO_4",
    name="CLO4",
    domain="DSA",
    subclassOf=CLO.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ),
        Attribute(
            name="description",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)


CLO5 = Concept(
    id="O_C_CLO_5",
    name="CLO5",
    domain="DSA",
    subclassOf=CLO.id,
    attributes=[
        Attribute(
            name="weight",
            value_type=ValueType.INTEGER,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        ),
        Attribute(
            name="description",
            value_type=ValueType.STRING,
            value_domain=None,
            cardinality=Cardinality.ONE_ONE,
            constraint=None
        )
    ],
    invariant=[],
    operation=[]
)