from MetaModel.classes.enums.types import ValueType, Cardinality
from MetaModel.classes import Concept, Attribute

Chapter=Concept(
    id="O_C_CHAPTER",
    name="Chapter",
    domain="DSA",
    subclassOf="",
    attributes=[],
    invariant=[],
    operation=[]
)

Chapter_Overview=Concept(
    id="O_C_CHAPTER_OVERVIEW",
    name="Overview",
    domain="DSA",
    subclassOf=Chapter.id,
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

Chapter_SearchingAndSorting=Concept(
    id="O_C_CHAPTER_SEARCHING_AND_SORTING",
    name="SearchingAndSorting",
    domain="DSA",
    subclassOf=Chapter.id,
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

Chapter_LinkList=Concept(
    id="O_C_CHAPTER_LINKLIST",
    name="LinkList",
    domain="DSA",
    subclassOf=Chapter.id,
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