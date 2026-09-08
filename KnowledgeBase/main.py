from Instance import all_instances
from Ontology.DSA_Ontology import dsa_ontology
from MetaModel import KnowledgeBase

dsa_knowledge_base = KnowledgeBase(
    ontology=dsa_ontology,
    instances=all_instances
)

import pprint
from dataclasses import asdict

def main():
    print("dsa_knowledge_base:")
    pprint.pprint(asdict(dsa_knowledge_base), sort_dicts=False)
    
if __name__ == "__main__":
    main()

