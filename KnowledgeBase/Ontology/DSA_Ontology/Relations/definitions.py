from MetaModel.classes.enums.types import Cardinality, ValueType
from MetaModel.classes.Relation import Relation
from Ontology.DSA_Ontology.Concepts.chapters import Chapter_Overview, Chapter_SearchingAndSorting, Chapter_LinkList
from Ontology.DSA_Ontology.Concepts.clos import CLO1, CLO2, CLO3, CLO4, CLO5

relations = [
    Relation(
        id="O_REL_CLO1_CHAPTER_OVERVIEW",
        name="linked",
        source=CLO1.id,
        cardinality=Cardinality.ONE_ONE,
        value_type=ValueType.CONCEPT,
        value_domain=[Chapter_Overview.id],
        constraint=None
    ),
    Relation(
        id="O_REL_CLO2_CHAPTER_SEARCHING_AND_SORTING",
        name="linked",
        source=CLO2.id,
        cardinality=Cardinality.ONE_ONE,
        value_type=ValueType.CONCEPT,
        value_domain=[Chapter_SearchingAndSorting.id],
        constraint=None
    ),  
    Relation(
        id="O_REL_CLO3_CHAPTER_SEARCHING_AND_SORTING",
        name="linked",
        source=CLO3.id,
        cardinality=Cardinality.ONE_ONE,
        value_type=ValueType.CONCEPT,
        value_domain=[Chapter_SearchingAndSorting.id],
        constraint=None
    ),
    Relation(
        id="O_REL_CLO4_CHAPTER_LINKLIST",
        name="linked",
        source=CLO4.id,
        cardinality=Cardinality.ONE_ONE,
        value_type=ValueType.CONCEPT,
        value_domain=[Chapter_LinkList.id],
        constraint=None
    ),
    Relation(
        id="O_REL_CLO5_CHAPTER_LINKLIST",
        name="linked",
        source=CLO5.id,
        cardinality=Cardinality.ONE_ONE,
        value_type=ValueType.CONCEPT,
        value_domain=[Chapter_LinkList.id],
        constraint=None
    )
]
