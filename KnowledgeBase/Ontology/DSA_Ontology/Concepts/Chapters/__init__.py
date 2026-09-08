from MetaModel.classes.enums.types import ValueType, Cardinality
from MetaModel.classes.Concept import Concept, Attribute

Chapter=Concept(
    id="O_C_CHAPTER",
    name="Chapter",
    domain="Chapter",
    subclassOf="",
    attributes=[],
    invariant=[],
    operation=[]
)

Overview=Concept(
    id="O_C_CHAPTER_OVERVIEW",
    name="Overview",
    domain="Chapter",
    subclassOf="O_C_CHAPTER",
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

SearchingAndSorting=Concept(
    id="O_C_CHAPTER_SEARCHING_AND_SORTING",
    name="SearchingAndSorting",
    domain="Chapter",
    subclassOf="O_C_CHAPTER",
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

LinkList=Concept(
    id="O_C_CHAPTER_LINKLIST",
    name="LinkList",
    domain="Chapter",
    subclassOf="O_C_CHAPTER",
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