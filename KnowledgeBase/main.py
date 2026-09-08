from Instance import all_instances
from Ontology.DSA_Ontology import dsa_ontology
from MetaModel import KnowledgeBase

dsa_knowledge_base = KnowledgeBase(
    ontology=dsa_ontology,
    instances=all_instances
)

def main():
    print("dsa_knowledge_base",dsa_knowledge_base)
    
if __name__ == "__main__":
    main()

