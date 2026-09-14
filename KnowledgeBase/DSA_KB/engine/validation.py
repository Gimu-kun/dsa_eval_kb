import os
import sys
from collections import Counter
from typing import Dict, List, Set, Tuple, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
dsa_kb_dir = os.path.dirname(current_dir)
kb_dir = os.path.dirname(dsa_kb_dir)
root_dir = os.path.dirname(kb_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from KnowledgeBase.DSA_KB.meta_model.classes.enums.types import ValueType, Cardinality, ConditionType
from KnowledgeBase.DSA_KB.meta_model.classes.Condition import Condition
from KnowledgeBase.DSA_KB.meta_model.classes.Attribute import AttributeDefinition, AttributeValue
from KnowledgeBase.DSA_KB.meta_model.classes.Rule import (
    Rule, ConclusionType, AttributeConclusion, RelationConclusion, ConceptConclusion
)

class KnowledgeValidator:
    def __init__(self, concepts, relations, instances, assertions, rules=None, hierarchy=None, functions=None, operands=None):
        self.concepts = concepts
        self.relations = relations
        self.instances = instances
        self.assertions = assertions
        self.rules = rules or []
        self.hierarchy = hierarchy or {}
        self.functions = functions or []
        self.operands = operands or []
        
        self.concept_map = {c.id: c for c in concepts}
        self.relation_map = {r.id: r for r in relations}
        self.instance_map = {i.id: i for i in instances}
        self.rule_map = {r.id: r for r in self.rules}
        self.function_map = {f.id: f for f in self.functions}
        self.operand_map = {op.id: op for op in self.operands if op.id}
        self.operand_var_map = {}
        for op in self.operands:
            if op.variable:
                self.operand_var_map[op.variable] = op
                clean_v = op.variable.replace("()", "")
                self.operand_var_map[clean_v] = op
        if "ques" not in self.operand_var_map and "O_C_QUESTION" in self.concept_map:
            from KnowledgeBase.DSA_KB.meta_model.classes.Operand import Operand
            self.operand_var_map["ques"] = Operand(id="OP_QUESTION", operand_type="concept", variable="ques", value="O_C_QUESTION")
        
        self.errors: List[str] = []
        self.warnings: List[str] = []

    # =========================================================================
    # 1. KIỂM TRA TRÙNG LẶP ID (ID DUPLICATION VALIDATION)
    # =========================================================================
    def validate_id_uniqueness(self):
        """Kiểm tra trùng lặp ID trong từng tập dữ liệu và xung đột giữa các tập."""
        # 1.1 Kiểm tra trùng lặp trong nội bộ từng tập dữ liệu
        concept_ids = [c.id for c in self.concepts if c.id]
        for cid, count in Counter(concept_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Concept] Mã Khái niệm '{cid}' bị định nghĩa trùng lặp {count} lần trong concepts.json")

        instance_ids = [i.id for i in self.instances if i.id]
        for iid, count in Counter(instance_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Instance] Mã Đối tượng '{iid}' bị định nghĩa trùng lặp {count} lần trong instances.json")

        relation_ids = [r.id for r in self.relations if r.id]
        for rid, count in Counter(relation_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Relation] Mã Quan hệ '{rid}' bị định nghĩa trùng lặp {count} lần trong relations.json")

        rule_ids = [r.id for r in self.rules if r.id]
        for ruid, count in Counter(rule_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Rule] Mã Luật '{ruid}' bị định nghĩa trùng lặp {count} lần trong rules.json")

        func_ids = [f.id for f in self.functions if f.id]
        for fid, count in Counter(func_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Function] Mã Hàm '{fid}' bị định nghĩa trùng lặp {count} lần trong functions.json")

        op_ids = [op.id for op in self.operands if op.id]
        for opid, count in Counter(op_ids).items():
            if count > 1:
                self.errors.append(f"[Trùng lặp ID - Operand] Mã Toán hạn '{opid}' bị định nghĩa trùng lặp {count} lần trong operands.json")

        # 1.2 Kiểm tra xung đột ID chéo giữa Khái niệm và Đối tượng
        cross_ci = set(concept_ids) & set(instance_ids)
        for cid in cross_ci:
            self.errors.append(f"[Xung đột ID chéo] ID '{cid}' vừa được dùng làm Khái niệm (Concept) vừa làm Đối tượng (Instance)")

        # 1.3 Kiểm tra trùng lặp các phán đoán hoàn toàn giống nhau (source, relation, target)
        assertion_tuples = [(a.source, a.relation, a.target) for a in self.assertions]
        for (src, rel, tgt), count in Counter(assertion_tuples).items():
            if count > 1:
                self.warnings.append(f"[Trùng lặp Phán đoán] Phán đoán ('{src}' --{rel}--> '{tgt}') bị lặp lại {count} lần trong assertions.json")

    # =========================================================================
    # 2. KIỂM TRA KHÁI NIỆM & VÒNG LẶP KẾ THỪA (CONCEPTS & CYCLE DETECTION)
    # =========================================================================
    def validate_concepts(self):
        for c in self.concepts:
            if not c.id:
                self.errors.append("[Concept] Phát hiện Khái niệm không có trường 'id'")
                continue
            if not c.name:
                self.warnings.append(f"[Concept] Khái niệm '{c.id}' thiếu trường tên 'name'")

            # Kiểm tra lớp cha subclass_of
            if c.subclass_of:
                if c.subclass_of not in self.concept_map:
                    self.errors.append(f"[Concept] Khái niệm '{c.id}' kế thừa lớp cha không tồn tại: '{c.subclass_of}'")
                else:
                    # Phát hiện vòng lặp kế thừa (Cycle Detection)
                    visited = [c.id]
                    curr = c.subclass_of
                    while curr:
                        if curr in visited:
                            cycle_path = " -> ".join(visited + [curr])
                            self.errors.append(f"[Vòng lặp Kế thừa] Phát hiện vòng lặp kế thừa (Inheritance Cycle) tại '{c.id}': {cycle_path}")
                            break
                        visited.append(curr)
                        parent = self.concept_map.get(curr)
                        curr = parent.subclass_of if parent else None

            # Kiểm tra định nghĩa thuộc tính của Concept
            for attr in c.attributes:
                if not attr.name:
                    self.errors.append(f"[Concept] Khái niệm '{c.id}' có thuộc tính không có tên 'name'")
                if not isinstance(attr.value_type, ValueType):
                    self.errors.append(f"[Concept] Khái niệm '{c.id}' thuộc tính '{attr.name}' có kiểu dữ liệu không hợp lệ: {attr.value_type}")

    def validate_hierarchy(self):
        """Kiểm tra tính hợp lệ của quan hệ kế thừa trong file hierarchy.json / hierarchy.json."""
        for sub, sup in self.hierarchy.items():
            if sub not in self.concept_map:
                self.errors.append(f"[Hierarchy] Khái niệm con (subclass) '{sub}' trong file hierarchy không tồn tại trong concepts.json")
            if sup not in self.concept_map:
                self.errors.append(f"[Hierarchy] Khái niệm cha (superclass) '{sup}' trong file hierarchy không tồn tại trong concepts.json")
            if sub == sup:
                self.errors.append(f"[Hierarchy] Phát hiện tự kế thừa chính mình: '{sub}' kế thừa '{sup}'")

    def get_all_attributes_for_concept(self, concept_id: str) -> Dict[str, AttributeDefinition]:
        """Lấy tất cả AttributeDefinition của một Concept (kể cả thừa kế), có bảo vệ chống lặp vô hạn."""
        attrs = {}
        visited = set()
        current_id = concept_id
        while current_id and current_id not in visited:
            visited.add(current_id)
            concept = self.concept_map.get(current_id)
            if not concept:
                break
            for attr in concept.attributes:
                if attr.name not in attrs:
                    attrs[attr.name] = attr
            current_id = concept.subclass_of
        return attrs

    def is_subclass_or_self(self, concept_id: str, target_id: str) -> bool:
        """Kiểm tra xem concept_id có phải là subclass của target_id không (có chống lặp vô hạn)."""
        visited = set()
        current_id = concept_id
        while current_id and current_id not in visited:
            if current_id == target_id:
                return True
            visited.add(current_id)
            concept = self.concept_map.get(current_id)
            current_id = concept.subclass_of if concept else None
        return False

    # =========================================================================
    # 3. KIỂM TRA ĐỐI TƯỢNG (INSTANCES VALIDATION)
    # =========================================================================
    def validate_type(self, attr_val: AttributeValue, expected_type: ValueType) -> bool:
        value = attr_val.value
        if value is None:
            return True

        if expected_type == ValueType.INTEGER:
            if isinstance(value, int) and not isinstance(value, bool):
                return True
            try:
                attr_val.value = int(value)
                return True
            except (ValueError, TypeError):
                return False

        if expected_type == ValueType.FLOAT:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if isinstance(value, int):
                    attr_val.value = float(value)
                return True
            try:
                attr_val.value = float(value)
                return True
            except (ValueError, TypeError):
                return False

        if expected_type == ValueType.STRING:
            if isinstance(value, str):
                return True
            attr_val.value = str(value)
            return True

        if expected_type == ValueType.BOOLEAN:
            if isinstance(value, bool):
                return True
            if isinstance(value, str):
                lower_val = value.lower().strip()
                if lower_val in ("true", "1", "yes"):
                    attr_val.value = True
                    return True
                elif lower_val in ("false", "0", "no"):
                    attr_val.value = False
                    return True
            if isinstance(value, int) and value in (0, 1):
                attr_val.value = bool(value)
                return True
            return False

        if expected_type == ValueType.CONCEPT:
            return str(value) in self.concept_map or str(value) in self.instance_map

        return True

    def evaluate_condition(self, value, condition: Condition) -> bool:
        if not condition:
            return True
            
        if condition.condition_type == ConditionType.DOMAIN:
            op = condition.operator
            if op in ("RANGE", "BETWEEN"):
                if len(condition.operands) >= 2:
                    min_val = condition.operands[0].value
                    max_val = condition.operands[1].value
                    try:
                        return float(min_val) <= float(value) <= float(max_val)
                    except:
                        return False
            elif op in ("ENUM", "IN"):
                valid_values = [str(opnd.value).lower() for opnd in condition.operands]
                return str(value).lower() in valid_values
            elif op == "NOT_IN":
                valid_values = [str(opnd.value).lower() for opnd in condition.operands]
                return str(value).lower() not in valid_values
                
        if condition.condition_type == ConditionType.COMPARISON:
            op = condition.operator
            target_val = None
            for opnd in condition.operands:
                if hasattr(opnd, "operand_type") and opnd.operand_type != ValueType.VARIABLE:
                    target_val = opnd.value
                    break
            if target_val is not None:
                try:
                    num_val = float(value)
                    num_tgt = float(target_val)
                    if op == "GT": return num_val > num_tgt
                    elif op == "GTE": return num_val >= num_tgt
                    elif op == "LT": return num_val < num_tgt
                    elif op == "LTE": return num_val <= num_tgt
                    elif op == "EQ": return num_val == num_tgt
                    elif op == "NEQ": return num_val != num_tgt
                except:
                    pass

        return True

    def validate_instances(self):
        for instance in self.instances:
            if not instance.id:
                self.errors.append("[Instance] Phát hiện Đối tượng không có trường 'id'")
                continue
            if not instance.instanceOf:
                self.errors.append(f"[Instance] Đối tượng '{instance.id}' thiếu trường 'instanceOf'")
                continue
            if instance.instanceOf not in self.concept_map:
                self.errors.append(f"[Instance] Đối tượng '{instance.id}' tham chiếu khái niệm không tồn tại: '{instance.instanceOf}'")
                continue
                
            expected_attrs = self.get_all_attributes_for_concept(instance.instanceOf)
            actual_attrs = {a.name: a for a in instance.attributes if a.name}
            
            # Kiểm tra thuộc tính bắt buộc (required: True)
            for attr_name, attr_def in expected_attrs.items():
                if attr_def.required:
                    if attr_name not in actual_attrs or actual_attrs[attr_name].value in (None, ""):
                        self.errors.append(
                            f"[Instance Thiếu Thuộc Tính Bắt Buộc] Đối tượng '{instance.id}' thiếu giá trị cho thuộc tính bắt buộc '{attr_name}' "
                            f"(định nghĩa bởi Khái niệm '{instance.instanceOf}')"
                        )
                    
            # Kiểm tra kiểu dữ liệu và ràng buộc của các giá trị thực tế
            for attr_name, attr_val in actual_attrs.items():
                if attr_name not in expected_attrs:
                    self.warnings.append(
                        f"[Instance Thuộc Tính Ngoài Dự Kiến] Đối tượng '{instance.id}' có thuộc tính '{attr_name}' "
                        f"không được định nghĩa trong lược đồ Khái niệm '{instance.instanceOf}'"
                    )
                    continue
                
                attr_def = expected_attrs[attr_name]
                if not self.validate_type(attr_val, attr_def.value_type):
                    self.errors.append(
                        f"[Instance Sai Kiểu Dữ Liệu] Đối tượng '{instance.id}' thuộc tính '{attr_name}' sai kiểu. "
                        f"Kỳ vọng {attr_def.value_type.value}, nhận được giá trị '{attr_val.value}'"
                    )
                
                if attr_def.constraint:
                    constraints = attr_def.constraint if isinstance(attr_def.constraint, list) else [attr_def.constraint]
                    for c in constraints:
                        if not self.evaluate_condition(attr_val.value, c):
                            self.errors.append(
                                f"[Instance Vi Phạm Ràng Buộc] Đối tượng '{instance.id}' thuộc tính '{attr_name}' "
                                f"vi phạm ràng buộc '{c.operator}' với giá trị '{attr_val.value}'"
                            )

    # =========================================================================
    # 4. KIỂM TRA QUAN HỆ & PHÁN ĐOÁN (RELATIONS & ASSERTIONS VALIDATION)
    # =========================================================================
    def validate_relations(self):
        for r in self.relations:
            if not r.id:
                self.errors.append("[Relation] Phát hiện Quan hệ không có 'id'")
                continue
            sources = r.source if isinstance(r.source, list) else [s.strip() for s in r.source.split(",")] if isinstance(r.source, str) else []
            for s in sources:
                if s not in self.concept_map:
                    self.errors.append(f"[Relation] Quan hệ '{r.id}' có miền nguồn (source) '{s}' không tồn tại trong concepts.json")
            targets = r.target if isinstance(r.target, list) else [t.strip() for t in r.target.split(",")] if isinstance(r.target, str) else []
            for t in targets:
                if t not in self.concept_map:
                    self.errors.append(f"[Relation] Quan hệ '{r.id}' có miền đích (target) '{t}' không tồn tại trong concepts.json")
            if not isinstance(r.cardinality, Cardinality):
                self.errors.append(f"[Relation] Quan hệ '{r.id}' có bản số (cardinality) không hợp lệ: '{r.cardinality}'")

    def validate_assertions(self):
        assertion_counts = {r.id: {} for r in self.relations}
        
        for idx, assertion in enumerate(self.assertions):
            if assertion.relation not in self.relation_map:
                self.errors.append(f"[Assertion #{idx}] Tham chiếu quan hệ không tồn tại: '{assertion.relation}'")
                continue
                
            relation = self.relation_map[assertion.relation]
            
            # Kiểm tra thực thể nguồn (Source)
            source_inst = self.instance_map.get(assertion.source)
            source_concept = self.concept_map.get(assertion.source)
            if not source_inst and not source_concept:
                self.errors.append(f"[Assertion #{idx}] Thực thể nguồn '{assertion.source}' không tìm thấy trong instances hay concepts")
            else:
                source_type = source_inst.instanceOf if source_inst else source_concept.id
                sources = relation.source if isinstance(relation.source, list) else [s.strip() for s in relation.source.split(",")] if isinstance(relation.source, str) else [relation.source]
                if not any(self.is_subclass_or_self(source_type, s) for s in sources):
                    self.errors.append(
                        f"[Assertion #{idx} Lệch Nguồn (Domain)] Nguồn '{assertion.source}' (kiểu '{source_type}') "
                        f"không phải là lớp con của miền nguồn '{relation.source}' trong quan hệ '{relation.id}'"
                    )
                    
            # Kiểm tra thực thể đích (Target)
            target_inst = self.instance_map.get(assertion.target)
            target_concept = self.concept_map.get(assertion.target)
            if not target_inst and not target_concept:
                self.errors.append(f"[Assertion #{idx}] Thực thể đích '{assertion.target}' không tìm thấy trong instances hay concepts")
            else:
                target_type = target_inst.instanceOf if target_inst else target_concept.id
                targets = relation.target if isinstance(relation.target, list) else [t.strip() for t in relation.target.split(",")] if isinstance(relation.target, str) else [relation.target]
                if not any(self.is_subclass_or_self(target_type, t) for t in targets):
                    self.errors.append(
                        f"[Assertion #{idx} Lệch Đích (Range)] Đích '{assertion.target}' (kiểu '{target_type}') "
                        f"không phải là lớp con của miền đích '{relation.target}' trong quan hệ '{relation.id}'"
                    )
                    
            # Đếm bản số cardinality
            if assertion.source not in assertion_counts[relation.id]:
                assertion_counts[relation.id][assertion.source] = 0
            assertion_counts[relation.id][assertion.source] += 1
            
            # Kiểm tra thuộc tính của assertion nếu relation có attributes
            expected_attrs = {a.name: a for a in relation.attributes}
            actual_attrs = {a.name: a for a in assertion.attributes}
            
            for attr_name, attr_val in actual_attrs.items():
                if attr_name not in expected_attrs:
                    self.warnings.append(
                        f"[Assertion #{idx}] Phán đoán giữa '{assertion.source}' và '{assertion.target}' "
                        f"có thuộc tính ngoài dự kiến '{attr_name}' cho quan hệ '{assertion.relation}'"
                    )
                    continue
                
                attr_def = expected_attrs[attr_name]
                if not self.validate_type(attr_val, attr_def.value_type):
                    self.errors.append(
                        f"[Assertion #{idx}] Thuộc tính '{attr_name}' sai kiểu dữ liệu. "
                        f"Kỳ vọng {attr_def.value_type.value}, nhận được '{attr_val.value}'"
                    )
                
                if attr_def.constraint:
                    constraints = attr_def.constraint if isinstance(attr_def.constraint, list) else [attr_def.constraint]
                    for c in constraints:
                        if not self.evaluate_condition(attr_val.value, c):
                            self.errors.append(
                                f"[Assertion #{idx}] Thuộc tính '{attr_name}' vi phạm ràng buộc "
                                f"'{c.operator}' với giá trị '{attr_val.value}'"
                            )

        # Kiểm tra bản số Cardinality
        for relation in self.relations:
            # Tìm các instances thuộc miền source của relation
            valid_sources = [i.id for i in self.instances if self.is_subclass_or_self(i.instanceOf, relation.source)]
            counts = assertion_counts[relation.id]
            
            for src_id in valid_sources:
                count = counts.get(src_id, 0)
                cardinality = relation.cardinality
                if cardinality == Cardinality.ONE_ONE and count != 1:
                    self.warnings.append(
                        f"[Bản số Cardinality] Quan hệ '{relation.id}' yêu cầu đúng 1 liên kết (1..1) "
                        f"cho nguồn '{src_id}', nhưng hiện có {count} liên kết"
                    )
                elif cardinality == Cardinality.ONE_MANY and count < 1:
                    self.warnings.append(
                        f"[Bản số Cardinality] Quan hệ '{relation.id}' yêu cầu ít nhất 1 liên kết (1..*) "
                        f"cho nguồn '{src_id}', nhưng hiện có {count} liên kết"
                    )
                elif cardinality == Cardinality.ZERO_ONE and count > 1:
                    self.errors.append(
                        f"[Bản số Cardinality] Quan hệ '{relation.id}' chỉ cho phép tối đa 1 liên kết (0..1) "
                        f"cho nguồn '{src_id}', nhưng hiện có {count} liên kết"
                    )

    # =========================================================================
    # 5. KIỂM TRA LUẬT SUY DIỄN (RULES VALIDATION)
    # =========================================================================
    def validate_rules(self):
        for r in self.rules:
            if not r.id:
                self.errors.append("[Rule] Phát hiện Luật không có trường 'id'")
                continue
            if not r.condition:
                self.errors.append(f"[Rule] Luật '{r.id}' thiếu định nghĩa điều kiện 'condition'")
            if not r.conclusion:
                self.errors.append(f"[Rule] Luật '{r.id}' thiếu định nghĩa kết luận 'conclusion'")
            else:
                for idx, c in enumerate(r.conclusion):
                    if isinstance(c, AttributeConclusion):
                        valid_targets = set(self.instance_map.keys()) | set(self.concept_map.keys()) | set(self.operand_var_map.keys())
                        if c.target_instance and c.target_instance not in valid_targets:
                            self.warnings.append(f"[Rule #{r.id}] Kết luận #{idx} tham chiếu thực thể đích '{c.target_instance}' chưa có trong KB hoặc tập Toán hạn")
                    elif isinstance(c, RelationConclusion):
                        if c.relation_id and c.relation_id not in self.relation_map:
                            self.errors.append(f"[Rule #{r.id}] Kết luận #{idx} tham chiếu quan hệ '{c.relation_id}' không tồn tại")

    # =========================================================================
    # 6. KIỂM TRA TẬP HÀM (FUNCTIONS VALIDATION)
    # =========================================================================
    def validate_functions(self):
        for f in self.functions:
            if not f.id:
                self.errors.append("[Function] Phát hiện Hàm không có trường 'id'")
                continue
            if not f.name:
                self.warnings.append(f"[Function] Hàm '{f.id}' thiếu trường tên 'name'")

    # =========================================================================
    # 7. KIỂM TRA TẬP TOÁN HẠN (OPERANDS VALIDATION)
    # =========================================================================
    def validate_operands(self):
        for op in self.operands:
            if not op.id:
                self.errors.append("[Operand] Phát hiện Toán hạn không có trường 'id'")
                continue
            if not op.operand_type:
                self.warnings.append(f"[Operand #{op.id}] Toán hạn thiếu kiểu 'operandType'")
            if op.operand_type == "concept" and op.value:
                if op.value not in self.concept_map:
                    self.errors.append(f"[Operand #{op.id}] Giá trị khái niệm '{op.value}' không tồn tại trong concepts.json")
            elif op.operand_type == "function" and op.value:
                if op.value not in self.function_map:
                    self.errors.append(f"[Operand #{op.id}] Giá trị hàm '{op.value}' không tồn tại trong functions.json")

    # =========================================================================
    # MAIN VALIDATION EXECUTION & REPORTING
    # =========================================================================
    def validate(self) -> bool:
        self.errors = []
        self.warnings = []
        
        # 1. Trùng lặp ID
        self.validate_id_uniqueness()
        # 2. Khái niệm & Kế thừa
        self.validate_concepts()
        self.validate_hierarchy()
        # 3. Đối tượng
        self.validate_instances()
        # 4. Quan hệ & Phán đoán
        self.validate_relations()
        self.validate_assertions()
        # 5. Luật suy diễn
        self.validate_rules()
        # 6. Tập hàm
        self.validate_functions()
        # 7. Tập toán hạn
        self.validate_operands()
        
        total_issues = len(self.errors) + len(self.warnings)
        
        print("\n" + "=" * 80)
        print(" BÁO CÁO KIỂM TRA TOÀN DIỆN KNOWLEDGE BASE (VALIDATION REPORT)")
        print("=" * 80)
        print(f" • Tổng số Khái niệm (Concepts):    {len(self.concepts)}")
        print(f" • Tổng số Quan hệ Kế thừa:         {len(self.hierarchy)}")
        print(f" • Tổng số Đối tượng (Instances):   {len(self.instances)}")
        print(f" • Tổng số Quan hệ (Relations):     {len(self.relations)}")
        print(f" • Tổng số Phán đoán (Assertions):  {len(self.assertions)}")
        print(f" • Tổng số Luật (Rules):            {len(self.rules)}")
        print(f" • Tổng số Hàm (Functions):         {len(self.functions)}")
        print(f" • Tổng số Toán hạn (Operands):     {len(self.operands)}")
        print("-" * 80)
        
        if self.errors:
            print(f"\n❌ PHÁT HIỆN {len(self.errors)} LỖI NGHIÊM TRỌNG (ERRORS):")
            for idx, err in enumerate(self.errors, 1):
                print(f"  {idx:2d}. {err}")
                
        if self.warnings:
            print(f"\n⚠️  PHÁT HIỆN {len(self.warnings)} CẢNH BÁO (WARNINGS):")
            for idx, warn in enumerate(self.warnings, 1):
                print(f"  {idx:2d}. {warn}")
                
        print("\n" + "=" * 80)
        if not self.errors:
            print("✅ KẾT QUẢ: KIỂM TRA HỢP LỆ! Không có lỗi nghiêm trọng.")
            print("=" * 80 + "\n")
            return True
        else:
            print(f"🛑 KẾT QUẢ: KHÔNG HỢP LỆ! Có {len(self.errors)} lỗi cần khắc phục.")
            print("=" * 80 + "\n")
            return False

if __name__ == "__main__":
    from KnowledgeBase.DSA_KB.engine.loader import DsaKbLoader
    ontology_dir = os.path.join(dsa_kb_dir, "ontology")
    
    print("Đang nạp toàn bộ dữ liệu Knowledge Base...")
    loader = DsaKbLoader(ontology_dir)
    concepts = loader.load_concepts()
    relations = loader.load_relations()
    instances = loader.load_instances()
    assertions = loader.load_assertions()
    rules = loader.load_rules()
    hierarchy = loader.load_hierarchy()
    functions = loader.load_functions()
    operands = loader.load_operands()
    
    validator = KnowledgeValidator(concepts, relations, instances, assertions, rules, hierarchy=hierarchy, functions=functions, operands=operands)
    validator.validate()
