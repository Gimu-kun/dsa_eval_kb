from MetaModel import Instance
from Ontology.DSA_Ontology.Concepts.chapters import ( 
    Chapter_Overview, 
    Chapter_SearchingAndSorting, 
    Chapter_LinkList)

chapter_overview_instance = Instance(
    id="I_CHAPTER_OVERVIEW",
    concept_id=Chapter_Overview.id,
    attributes={
        "weight": 1
    }
)

chapter_searching_and_sorting_instance = Instance(
    id="I_CHAPTER_SEARCHING_AND_SORTING",
    concept_id=Chapter_SearchingAndSorting.id,
    attributes={
        "weight": 2
    }
)

chapter_linklist_instance = Instance(
    id="I_CHAPTER_LINKLIST",
    concept_id=Chapter_LinkList.id,
    attributes={
        "weight": 3
    }
)