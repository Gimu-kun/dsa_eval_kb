import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
dsa_kb_dir = os.path.dirname(current_dir)
kb_dir = os.path.dirname(dsa_kb_dir)
root_dir = os.path.dirname(kb_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from KnowledgeBase.DSA_KB.meta_model.classes import Concept, Relation, Rule, Operation
from KnowledgeBase.DSA_KB.meta_model.classes.Instance import Instance
from KnowledgeBase.DSA_KB.meta_model.classes.Assertion import Assertion
from KnowledgeBase.DSA_KB.meta_model.classes.Hierarchy import Hierarchy
from KnowledgeBase.DSA_KB.meta_model.classes.Attribute import AttributeDefinition, AttributeValue
from KnowledgeBase.DSA_KB.meta_model.classes.Condition import Condition
from KnowledgeBase.DSA_KB.meta_model.classes.Operand import Operand
from KnowledgeBase.DSA_KB.meta_model.classes.enums.types import ValueType, Cardinality, ConditionType
from KnowledgeBase.DSA_KB.meta_model import Ontology, KnowledgeBase

def parse_condition(cond_data: dict) -> Condition:
    if not cond_data:
        return None
    operator = cond_data.get("operator")
    cond_type_str = cond_data.get("condition_type", "Domain").upper()
    try:
        cond_type = ConditionType[cond_type_str]
    except KeyError:
        # Fallback
        cond_type = next((c for c in ConditionType if c.value == cond_data.get("condition_type")), ConditionType.DOMAIN)
        
    operands_data = cond_data.get("operands", [])
    operands = []
    for op_data in operands_data:
        if "operator" in op_data:
            # Nested condition
            operands.append(parse_condition(op_data))
        else:
            op_type_str = op_data.get("type", "string").upper()
            try:
                op_type = ValueType[op_type_str]
            except KeyError:
                op_type = next((v for v in ValueType if v.value == op_data.get("type")), ValueType.STRING)
            operands.append(Operand(operand_type=op_type, value=op_data.get("value")))
    return Condition(condition_type=cond_type, operator=operator, operands=operands)

def parse_attribute_definition(attr_data: dict) -> AttributeDefinition:
    val_type_str = attr_data.get("value_type", "str").upper()
    try:
        val_type = ValueType[val_type_str]
    except KeyError:
        val_type = next((v for v in ValueType if v.value == attr_data.get("value_type")), ValueType.STRING)

    constraint_data = attr_data.get("constraint")
    constraint = None
    if isinstance(constraint_data, list) and len(constraint_data) > 0:
        constraint = parse_condition(constraint_data[0])
    elif isinstance(constraint_data, dict):
        constraint = parse_condition(constraint_data)
        
    return AttributeDefinition(
        name=attr_data.get("name"),
        value_type=val_type,
        required=bool(attr_data.get("required", False)),
        constraint=constraint
    )

def parse_attribute_value(attr_data: dict) -> AttributeValue:
    return AttributeValue(
        name=attr_data.get("name"),
        value=attr_data.get("value")
    )

def parse_rule_conclusion(c_data: dict):
    from KnowledgeBase.DSA_KB.meta_model.classes.Rule import (
        ConclusionType, AttributeConclusion, RelationConclusion, ConceptConclusion
    )
    c_type_str = c_data.get("type", "attribute").lower()
    if c_type_str == "attribute":
        return AttributeConclusion(
            type=ConclusionType.ATTRIBUTE,
            target_instance=c_data.get("target_instance", ""),
            attribute_name=c_data.get("attribute_name", ""),
            valueType=c_data.get("valueType", ""),
            value=c_data.get("value")
        )
    elif c_type_str == "assertion":
        attrs = [parse_attribute_value(a) for a in c_data.get("attributes", [])]
        return RelationConclusion(
            type=ConclusionType.ASSERTION,
            source_instance=c_data.get("source_instance", ""),
            relation_id=c_data.get("relation_id", ""),
            target_instance=c_data.get("target_instance", ""),
            attributes=attrs
        )
    elif c_type_str == "instance":
        attrs = [parse_attribute_value(a) for a in c_data.get("attributes", [])]
        return ConceptConclusion(
            type=ConclusionType.INSTANCE,
            target_instance=c_data.get("target_instance", ""),
            attributes=attrs
        )
    return c_data

class DsaKbLoader:
    def __init__(self, ontology_dir: str):
        self.ontology_dir = ontology_dir

    def load_hierarchies(self) -> list[Hierarchy]:
        path = os.path.join(self.ontology_dir, "hierachy.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        h_list = data.get("hierarchy", []) or data.get("hierarchies", [])
        hierarchies = []
        for item in h_list:
            sub = item.get("subclass") or item.get("subclassOf")
            sup = item.get("superclass") or item.get("parent")
            if sub and sup:
                hierarchies.append(Hierarchy(subclass=sub, superclass=sup))
        return hierarchies

    def load_hierarchy(self) -> dict[str, str]:
        return {h.subclass: h.superclass for h in self.load_hierarchies()}

    def load_concepts(self) -> list[Concept]:
        hierarchy_map = self.load_hierarchy()
        path = os.path.join(self.ontology_dir, "concepts.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        concepts = []
        for c in data.get("concepts", []):
            attrs = [parse_attribute_definition(a) for a in c.get("attributes", [])]
            subclass_of = hierarchy_map.get(c.get("id")) or c.get("subclassOf")
            concept = Concept(
                id=c.get("id"),
                name=c.get("name"),
                domain=c.get("domain"),
                subclass_of=subclass_of,
                attributes=attrs,
                invariant=[],
                operation=[]
            )
            concepts.append(concept)
        return concepts

    def load_relations(self) -> list[Relation]:
        path = os.path.join(self.ontology_dir, "relations.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        relations = []
        for r in data.get("relations", []):
            card_str = r.get("cardinality")
            try:
                card = next((c for c in Cardinality if c.value == card_str), Cardinality.ONE_MANY)
            except:
                card = Cardinality.ONE_MANY
                
            attrs = [parse_attribute_definition(a) for a in r.get("attributes", [])]
            constraint = parse_condition(r.get("constraint"))
            
            relation = Relation(
                id=r.get("id"),
                name=r.get("name"),
                source=r.get("source"),
                target=r.get("target"),
                cardinality=card,
                attributes=attrs,
                constraint=constraint
            )
            relations.append(relation)
        return relations

    def load_instances(self) -> list[Instance]:
        path = os.path.join(self.ontology_dir, "instances.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        instances = []
        for i in data.get("instances", []):
            attrs = [parse_attribute_value(a) for a in i.get("attributes", [])]
            instance = Instance(
                id=i.get("id"),
                instanceOf=i.get("instanceOf"),
                attributes=attrs
            )
            instances.append(instance)
        return instances

    def load_assertions(self) -> list[Assertion]:
        path = os.path.join(self.ontology_dir, "assertions.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assertions = []
        for a in data.get("assertions", []):
            attrs = [parse_attribute_value(attr) for attr in a.get("attributes", [])]
            assertion = Assertion(
                source=a.get("source"),
                relation=a.get("relation"),
                target=a.get("target"),
                attributes=attrs
            )
            assertions.append(assertion)
        return assertions

    def load_rules(self) -> list[Rule]:
        path = os.path.join(self.ontology_dir, "rules.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = []
        for r in data.get("rules", []):
            cond = parse_condition(r.get("condition"))
            conclusions = [parse_rule_conclusion(c) for c in r.get("conclusion", [])]
            rule = Rule(
                id=r.get("id"),
                name=r.get("name"),
                condition=cond,
                conclusion=conclusions
            )
            rules.append(rule)
        return rules

    def load_ontology(self) -> Ontology:
        return Ontology(
            concepts=self.load_concepts(),
            hierarchies=self.load_hierarchies(),
            relations=self.load_relations(),
            rules=self.load_rules()
        )

    def load_kb(self) -> KnowledgeBase:
        return KnowledgeBase(
            ontology=self.load_ontology(),
            instances=self.load_instances(),
            assertions=self.load_assertions()
        )

