
from MetaModel import Ontology
from .Concepts import concepts
from .Relations import relations
from .Rules import rules
from .Operations import operations

dsa_ontology = Ontology(
    concepts,
    relations,
    rules,
    operations
)