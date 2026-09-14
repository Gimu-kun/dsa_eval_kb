import json
import os
import sys
from typing import Optional, List, Union

current_dir = os.path.dirname(os.path.abspath(__file__))
dsa_kb_dir = os.path.dirname(current_dir)
kb_dir = os.path.dirname(dsa_kb_dir)
root_dir = os.path.dirname(kb_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from KnowledgeBase.DSA_KB.meta_model.classes import (
    Concept, Relation, Rule, Operation, Function, Invariant, Parameter
)
from KnowledgeBase.DSA_KB.meta_model.classes.Instance import Instance
from KnowledgeBase.DSA_KB.meta_model.classes.Assertion import Assertion
from KnowledgeBase.DSA_KB.meta_model.classes.Hierarchy import Hierarchy
from KnowledgeBase.DSA_KB.meta_model.classes.Attribute import AttributeDefinition, AttributeValue
from KnowledgeBase.DSA_KB.meta_model.classes.Condition import Condition
from KnowledgeBase.DSA_KB.meta_model.classes.Operand import Operand
from KnowledgeBase.DSA_KB.meta_model.classes.enums.types import ValueType, Cardinality, ConditionType
from KnowledgeBase.DSA_KB.meta_model import Ontology, KnowledgeBase, DataLayer

def parse_condition(cond_data: Union[dict, str, None]) -> Optional[Condition]:
    if not cond_data:
        return None
    if isinstance(cond_data, str):
        return Condition(
            condition_type=ConditionType.LOGICAL,
            operator="EXPR",
            operands=[Operand(operand_type="expression", value=cond_data)]
        )
    operator = cond_data.get("operator")
    cond_type_str = str(cond_data.get("condition_type", "Domain")).upper()
    try:
        cond_type = ConditionType[cond_type_str]
    except KeyError:
        cond_type = next((c for c in ConditionType if c.value.lower() == str(cond_data.get("condition_type", "")).lower()), ConditionType.DOMAIN)
        
    operands_data = cond_data.get("operands", [])
    operands = []
    for op_data in operands_data:
        if isinstance(op_data, dict) and ("operator" in op_data or "condition_type" in op_data):
            # Nested condition
            operands.append(parse_condition(op_data))
        elif isinstance(op_data, dict):
            raw_type = op_data.get("operand_type") or op_data.get("operandType") or op_data.get("type", "string")
            operands.append(Operand(
                id=op_data.get("id"),
                operand_type=str(raw_type),
                variable=op_data.get("variable"),
                value=str(op_data.get("value", ""))
            ))
        else:
            operands.append(Operand(operand_type="string", value=str(op_data)))
    return Condition(condition_type=cond_type, operator=operator, operands=operands)

def parse_attribute_definition(attr_data: dict) -> AttributeDefinition:
    val_type_str = attr_data.get("value_type", "str").upper()
    try:
        val_type = ValueType[val_type_str]
    except KeyError:
        val_type = next((v for v in ValueType if v.value == attr_data.get("value_type")), ValueType.STRING)

    constraint_data = attr_data.get("constraint")
    constraints = []
    if isinstance(constraint_data, list):
        for item in constraint_data:
            cond = parse_condition(item)
            if cond:
                constraints.append(cond)
    elif isinstance(constraint_data, dict):
        cond = parse_condition(constraint_data)
        if cond:
            constraints.append(cond)
        
    return AttributeDefinition(
        name=attr_data.get("name"),
        value_type=val_type,
        required=bool(attr_data.get("required", False)),
        constraint=constraints
    )

def parse_attribute_value(attr_data: dict) -> AttributeValue:
    return AttributeValue(
        name=attr_data.get("name"),
        value=attr_data.get("value")
    )

def parse_parameter(p_data: dict) -> Parameter:
    if not p_data:
        return Parameter(name="", value_type="any", required=True)
    return Parameter(
        name=p_data.get("name", ""),
        value_type=p_data.get("valueType") or p_data.get("value_type", "any"),
        required=bool(p_data.get("required", True))
    )

def parse_operation(op_data: dict) -> Operation:
    inputs = [parse_parameter(p) for p in op_data.get("input", [])] if op_data.get("input") else []
    raw_out = op_data.get("output")
    outputs = None
    if isinstance(raw_out, list):
        outputs = [parse_parameter(p) for p in raw_out]
    elif isinstance(raw_out, dict):
        outputs = parse_parameter(raw_out)
    return Operation(
        name=op_data.get("name", ""),
        description=op_data.get("description"),
        input=inputs,
        output=outputs
    )

def parse_invariant(inv_data: dict) -> Invariant:
    return Invariant(
        name=inv_data.get("name", ""),
        condition=parse_condition(inv_data.get("condition")),
        description=inv_data.get("description")
    )

def parse_function(fn_data: dict) -> Function:
    inputs = [parse_parameter(p) for p in fn_data.get("input", [])] if fn_data.get("input") else []
    raw_out = fn_data.get("output")
    output = None
    if isinstance(raw_out, list):
        output = [parse_parameter(p) for p in raw_out]
    elif isinstance(raw_out, dict):
        output = parse_parameter(raw_out)
    return Function(
        id=fn_data.get("id", ""),
        name=fn_data.get("name", ""),
        input=inputs,
        output=output,
        description=fn_data.get("description")
    )

def parse_rule_conclusion(c_data: dict):
    from KnowledgeBase.DSA_KB.meta_model.classes.Rule import (
        ConclusionType, AttributeConclusion, RelationConclusion, ConceptConclusion
    )
    c_type_str = c_data.get("type", "attribute").lower()
    if c_type_str == "attribute":
        raw_val = c_data.get("value")
        val_type = c_data.get("valueType", "")
        if val_type == "bool" and isinstance(raw_val, str):
            val = raw_val.lower() == "true"
        else:
            val = raw_val
        return AttributeConclusion(
            type=ConclusionType.ATTRIBUTE,
            target_instance=c_data.get("target_instance", ""),
            attribute_name=c_data.get("attribute_name", ""),
            valueType=val_type,
            value=val
        )
    elif c_type_str in ("assertion", "relation"):
        attrs = [parse_attribute_value(a) for a in c_data.get("attributes", [])]
        return RelationConclusion(
            type=ConclusionType.ASSERTION,
            source_instance=c_data.get("source_instance", ""),
            relation_id=c_data.get("relation_id", ""),
            target_instance=c_data.get("target_instance", ""),
            attributes=attrs
        )
    elif c_type_str in ("instance", "concept"):
        attrs = [parse_attribute_value(a) for a in c_data.get("attributes", [])]
        return ConceptConclusion(
            type=ConclusionType.INSTANCE,
            target_instance=c_data.get("target_instance", ""),
            attributes=attrs
        )
    return c_data

class DsaKbLoader:
    def __init__(self, ontology_dir: str, data_dir: Optional[str] = None):
        self.ontology_dir = ontology_dir
        if data_dir:
            self.data_dir = data_dir
        else:
            parent_dir = os.path.dirname(self.ontology_dir)
            potential_data = os.path.join(parent_dir, "data")
            if os.path.exists(potential_data):
                self.data_dir = potential_data
            else:
                self.data_dir = self.ontology_dir

    def load_hierarchies(self) -> list[Hierarchy]:
        # Support both hierarchy.json and hierarchy.json
        path = os.path.join(self.ontology_dir, "hierarchy.json")
        if not os.path.exists(path):
            path = os.path.join(self.ontology_dir, "hierarchy.json")
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
            invariants = [parse_invariant(inv) for inv in c.get("invariant", [])]
            operations = [parse_operation(op) for op in c.get("operation", [])]
            subclass_of = hierarchy_map.get(c.get("id")) or c.get("subclassOf")
            concept = Concept(
                id=c.get("id"),
                name=c.get("name"),
                domain=c.get("domain"),
                subclass_of=subclass_of,
                attributes=attrs,
                invariant=invariants,
                operation=operations
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
            raw_constraint = r.get("constraint")
            constraints = []
            if isinstance(raw_constraint, list):
                for item in raw_constraint:
                    cond = parse_condition(item)
                    if cond:
                        constraints.append(cond)
            elif isinstance(raw_constraint, dict):
                cond = parse_condition(raw_constraint)
                if cond:
                    constraints.append(cond)
            
            relation = Relation(
                id=r.get("id"),
                name=r.get("name"),
                source=r.get("source"),
                target=r.get("target"),
                cardinality=card,
                attributes=attrs,
                constraint=constraints
            )
            relations.append(relation)
        return relations

    def load_functions(self) -> list[Function]:
        path = os.path.join(self.ontology_dir, "functions.json")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        functions = []
        for fn_data in data.get("functions", []):
            functions.append(parse_function(fn_data))
        return functions

    def load_instances(self) -> list[Instance]:
        instances_map = {}
        paths = [
            os.path.join(self.ontology_dir, "instances.json"),
            os.path.join(self.data_dir, "instances.json")
        ]
        for path in paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for i in data.get("instances", []):
                        iid = i.get("id")
                        if not iid:
                            continue
                        attrs = [parse_attribute_value(a) for a in i.get("attributes", [])]
                        instances_map[iid] = Instance(
                            id=iid,
                            instanceOf=i.get("instanceOf"),
                            attributes=attrs
                        )
                except Exception:
                    pass
        return list(instances_map.values())

    def load_assertions(self) -> list[Assertion]:
        all_assertions = []
        seen = set()
        paths = [
            os.path.join(self.ontology_dir, "assertions.json"),
            os.path.join(self.data_dir, "assertions.json")
        ]
        for path in paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for a in data.get("assertions", []):
                        key = (a.get("source"), a.get("relation"), a.get("target"))
                        if key not in seen:
                            seen.add(key)
                            attrs = [parse_attribute_value(attr) for attr in a.get("attributes", [])]
                            assertion = Assertion(
                                source=a.get("source"),
                                relation=a.get("relation"),
                                target=a.get("target"),
                                attributes=attrs
                            )
                            all_assertions.append(assertion)
                except Exception:
                    pass
        return all_assertions

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
                conclusion=conclusions,
                description=r.get("description"),
                expression=r.get("expression")
            )
            rules.append(rule)
        return rules

    def load_operands(self) -> list[Operand]:
        operands_map = {}
        paths = [
            os.path.join(self.ontology_dir, "operands.json"),
            os.path.join(self.data_dir, "operands.json")
        ]
        for path in paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for op in data.get("operands", []):
                        op_id = op.get("id")
                        if not op_id:
                            continue
                        operands_map[op_id] = Operand(
                            id=op_id,
                            operand_type=op.get("operandType") or op.get("operand_type"),
                            variable=op.get("variable"),
                            value=op.get("value")
                        )
                except Exception:
                    pass
        return list(operands_map.values())

    def load_ontology(self) -> Ontology:
        concepts = self.load_concepts()
        all_ops = []
        for c in concepts:
            if c.operation:
                all_ops.extend(c.operation)
        return Ontology(
            concepts=concepts,
            hierarchies=self.load_hierarchies(),
            relations=self.load_relations(),
            rules=self.load_rules(),
            functions=self.load_functions(),
            operations=all_ops,
            operands=self.load_operands()
        )

    def load_kb(self) -> KnowledgeBase:
        ontology = self.load_ontology()
        data = DataLayer(
            instances=self.load_instances(),
            assertions=self.load_assertions()
        )
        return KnowledgeBase(
            ontology=ontology,
            data=data
        )
