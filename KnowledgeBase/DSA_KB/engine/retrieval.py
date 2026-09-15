"""Truy hồi câu hỏi theo bộ lọc tùy chọn và nhánh ontology của topic.

Luồng:
1. Topic (nếu có) → nhánh cây: bản thân + tổ tiên (truy hồi ngược) + mọi lớp con.
2. Lọc câu hỏi theo Chương / Bloom / Độ khó / Dạng (mọi trường đều tùy chọn).
3. So khớp độ tương đồng câu hỏi ↔ topic, trả về tối đa 10 câu cao nhất.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
dsa_kb_dir = os.path.dirname(current_dir)
kb_dir = os.path.dirname(dsa_kb_dir)
root_dir = os.path.dirname(kb_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from KnowledgeBase.DSA_KB.engine.loader import DsaKbLoader
from KnowledgeBase.DSA_KB.meta_model import KnowledgeBase
from KnowledgeBase.DSA_KB.meta_model.classes.Concept import Concept
from KnowledgeBase.DSA_KB.meta_model.classes.Instance import Instance

REL_TYPE = "REL_QUESTION_HAS_QUESTION_TYPE"
REL_DIFF = "REL_QUESTION_HAS_DIFFICULTY"
REL_BLOOM = "REL_QUESTION_HAS_BLOOM_LEVEL"
REL_EA = "REL_QUESTION_HAS_EXPECTED_ANSWER"
REL_SCORE = "REL_EXPECTED_ANSWER_HAS_SCORING_RULE"
REL_CONCEPT = "REL_EXPECTED_RULE_REQUIRES_CONCEPT"

CHAPTER_IDS = {
    "c1": "O_C_CHAPTER_OVERVIEW",
    "1": "O_C_CHAPTER_OVERVIEW",
    "overview": "O_C_CHAPTER_OVERVIEW",
    "o_c_chapter_overview": "O_C_CHAPTER_OVERVIEW",
    "c2": "O_C_CHAPTER_SEARCHING_AND_SORTING",
    "2": "O_C_CHAPTER_SEARCHING_AND_SORTING",
    "searching": "O_C_CHAPTER_SEARCHING_AND_SORTING",
    "sorting": "O_C_CHAPTER_SEARCHING_AND_SORTING",
    "o_c_chapter_searching_and_sorting": "O_C_CHAPTER_SEARCHING_AND_SORTING",
    "c3": "O_C_CHAPTER_LINKED_LIST",
    "3": "O_C_CHAPTER_LINKED_LIST",
    "linked": "O_C_CHAPTER_LINKED_LIST",
    "o_c_chapter_linked_list": "O_C_CHAPTER_LINKED_LIST",
}
CHAPTER_PREFIX = {
    "O_C_CHAPTER_OVERVIEW": "C1",
    "O_C_CHAPTER_SEARCHING_AND_SORTING": "C2",
    "O_C_CHAPTER_LINKED_LIST": "C3",
}
BLOOM_IDS = {
    "r": "O_C_BLOOM_LEVEL_R",
    "remember": "O_C_BLOOM_LEVEL_R",
    "o_c_bloom_level_r": "O_C_BLOOM_LEVEL_R",
    "u": "O_C_BLOOM_LEVEL_U",
    "understand": "O_C_BLOOM_LEVEL_U",
    "o_c_bloom_level_u": "O_C_BLOOM_LEVEL_U",
    "ap": "O_C_BLOOM_LEVEL_AP",
    "a": "O_C_BLOOM_LEVEL_AP",
    "apply": "O_C_BLOOM_LEVEL_AP",
    "o_c_bloom_level_ap": "O_C_BLOOM_LEVEL_AP",
}
DIFF_IDS = {
    "e": "O_C_DIFFICULTY_EASY",
    "easy": "O_C_DIFFICULTY_EASY",
    "o_c_difficulty_easy": "O_C_DIFFICULTY_EASY",
    "m": "O_C_DIFFICULTY_MEDIUM",
    "medium": "O_C_DIFFICULTY_MEDIUM",
    "o_c_difficulty_medium": "O_C_DIFFICULTY_MEDIUM",
    "h": "O_C_DIFFICULTY_HARD",
    "hard": "O_C_DIFFICULTY_HARD",
    "o_c_difficulty_hard": "O_C_DIFFICULTY_HARD",
}
TYPE_IDS = {
    "des": "O_C_QUESTION_TYPE_DESCRIPTIVE",
    "descriptive": "O_C_QUESTION_TYPE_DESCRIPTIVE",
    "o_c_question_type_descriptive": "O_C_QUESTION_TYPE_DESCRIPTIVE",
    "pro": "O_C_QUESTION_TYPE_PROCEDURE",
    "procedure": "O_C_QUESTION_TYPE_PROCEDURE",
    "o_c_question_type_procedure": "O_C_QUESTION_TYPE_PROCEDURE",
    "app": "O_C_QUESTION_TYPE_APPLICATION",
    "application": "O_C_QUESTION_TYPE_APPLICATION",
    "o_c_question_type_application": "O_C_QUESTION_TYPE_APPLICATION",
}
Q_CODE = re.compile(r"^Q_(C[123])_(R|U|AP)_(DES|PRO|APP)_(E|M|H)$")
TOKEN_RE = re.compile(r"[0-9a-zA-Z_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", re.I)
STOPWORDS = {
    "la", "cua", "va", "mot", "cac", "trong", "voi", "khi", "thi", "cho", "den",
    "tu", "nay", "do", "duoc", "co", "khong", "hay", "mo", "ta", "the", "nao",
    "ve", "nhung", "neu", "hoac", "tren", "duoi", "sau", "truoc", "bang", "deu",
    "the", "a", "an", "the", "of", "and", "or", "to", "in", "on", "for", "is",
    "are", "be", "by", "with", "from",
}

CONCEPT_W = 0.62
TEXT_W = 0.38
MIN_SIMILARITY = 0.70


def _attr(obj, name, default=None):
    attrs = getattr(obj, "attributes", None) or []
    for a in attrs:
        if getattr(a, "name", None) == name:
            val = getattr(a, "value", None)
            if val not in (None, ""):
                return val
            d = getattr(a, "default", None)
            if d not in (None, ""):
                return d
    return default


def _fold(text: str) -> str:
    norm = unicodedata.normalize("NFD", text or "")
    return "".join(ch for ch in norm if unicodedata.category(ch) != "Mn").lower()


def _tokens(text: str) -> set[str]:
    toks = set()
    for raw in TOKEN_RE.findall(text or ""):
        folded = _fold(raw)
        if len(folded) < 2 or folded in STOPWORDS:
            continue
        toks.add(folded)
    return toks


def _norm_key(value: Optional[str]) -> str:
    if not value:
        return ""
    return _fold(str(value).strip()).replace(" ", "").replace("-", "_")


@dataclass
class QuestionFilter:
    chapter: Optional[str] = None
    bloom: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    limit: int = 10


@dataclass
class TopicBranch:
    topic_id: str
    topic_name: str
    ancestors: list[dict] = field(default_factory=list)
    descendants: list[dict] = field(default_factory=list)
    branch_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "topic_name": self.topic_name,
            "ancestors": self.ancestors,
            "descendants": self.descendants,
            "branch_ids": self.branch_ids,
        }


@dataclass
class RankedQuestion:
    question_id: str
    instance_id: str
    content: str
    chapter: str
    bloom: str
    question_type: str
    difficulty: str
    score: float
    concept_score: float
    text_score: float
    matched_concepts: list[str]
    expected_answer_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "instance_id": self.instance_id,
            "content": self.content,
            "chapter": self.chapter,
            "bloom": self.bloom,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "score": round(self.score, 4),
            "concept_score": round(self.concept_score, 4),
            "text_score": round(self.text_score, 4),
            "matched_concepts": self.matched_concepts,
            "expected_answer_id": self.expected_answer_id,
        }


@dataclass
class RetrievalResult:
    filters: dict
    branch: Optional[TopicBranch]
    candidate_count: int
    questions: list[RankedQuestion]

    def to_dict(self) -> dict:
        return {
            "filters": self.filters,
            "branch": self.branch.to_dict() if self.branch else None,
            "candidate_count": self.candidate_count,
            "questions": [q.to_dict() for q in self.questions],
        }


class RetrievalEngine:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.concept_map: dict[str, Concept] = {c.id: c for c in kb.ontology.concepts if c.id}
        self.instance_map: dict[str, Instance] = {i.id: i for i in kb.instances if i.id}
        self.parent_of: dict[str, str] = {}
        self.children_of: dict[str, list[str]] = defaultdict(list)
        for h in kb.ontology.hierarchies:
            if h.subclass and h.superclass:
                self.parent_of[h.subclass] = h.superclass
                self.children_of[h.superclass].append(h.subclass)

        self.assertions_from: dict[str, list] = defaultdict(list)
        for a in kb.assertions:
            self.assertions_from[a.source].append(a)

        self._questions = self._index_questions()

    def concept_label(self, concept_id: str) -> str:
        c = self.concept_map.get(concept_id)
        if not c:
            return concept_id
        if hasattr(c, "display_name"):
            return str(c.display_name())
        name = _attr(c, "name") or c.name or concept_id
        return str(name)

    def concept_text(self, concept_id: str) -> str:
        c = self.concept_map.get(concept_id)
        if not c:
            return concept_id
        parts = [concept_id, str(_attr(c, "name") or c.name or ""), str(_attr(c, "description") or "")]
        return " ".join(parts)

    def resolve_concept(self, raw: Optional[str]) -> Optional[str]:
        if not raw or not str(raw).strip():
            return None
        text = str(raw).strip()
        if text in self.concept_map:
            return text
        folded = _fold(text)
        compact = folded.replace(" ", "_")
        for cid in self.concept_map:
            if cid.lower() == text.lower() or cid.lower() == compact:
                return cid
        name_hits = []
        for cid, c in self.concept_map.items():
            label = _fold(str(_attr(c, "name") or c.name or ""))
            if label == folded:
                name_hits.append(cid)
        if len(name_hits) == 1:
            return name_hits[0]
        if name_hits:
            return sorted(name_hits, key=len)[0]
        contains = []
        for cid, c in self.concept_map.items():
            blob = _fold(self.concept_text(cid))
            if folded in blob:
                contains.append(cid)
        if not contains:
            return None
        dsa = [cid for cid in contains if getattr(self.concept_map[cid], "domain", "") == "DSA"]
        pool = dsa or contains
        return sorted(pool, key=lambda x: (0 if folded == _fold(self.concept_label(x)) else 1, len(x)))[0]

    def _resolve_alias(self, raw: Optional[str], table: dict[str, str]) -> Optional[str]:
        if not raw or not str(raw).strip():
            return None
        text = str(raw).strip()
        allowed = set(table.values())
        if text in allowed:
            return text
        key = _norm_key(text)
        if key in table:
            return table[key]
        resolved = self.resolve_concept(text)
        if resolved and resolved in allowed:
            return resolved
        return None

    def resolve_chapter(self, raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        text = str(raw).strip()
        if text in CHAPTER_PREFIX:
            return text
        return self._resolve_alias(text, CHAPTER_IDS)

    def resolve_bloom(self, raw: Optional[str]) -> Optional[str]:
        return self._resolve_alias(raw, BLOOM_IDS)

    def resolve_difficulty(self, raw: Optional[str]) -> Optional[str]:
        return self._resolve_alias(raw, DIFF_IDS)

    def resolve_question_type(self, raw: Optional[str]) -> Optional[str]:
        return self._resolve_alias(raw, TYPE_IDS)

    def topic_branch(self, topic: str) -> TopicBranch:
        topic_id = self.resolve_concept(topic)
        if not topic_id:
            raise ValueError(f"Không tìm thấy topic '{topic}' trong ontology.")

        ancestors = []
        seen = {topic_id}
        cur = self.parent_of.get(topic_id)
        depth = 1
        while cur and cur not in seen:
            seen.add(cur)
            ancestors.append({"id": cur, "name": self.concept_label(cur), "depth": depth})
            cur = self.parent_of.get(cur)
            depth += 1

        descendants = []
        stack = list(self.children_of.get(topic_id, []))
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            descendants.append({
                "id": node,
                "name": self.concept_label(node),
                "parent": self.parent_of.get(node),
            })
            stack.extend(self.children_of.get(node, []))

        descendants.sort(key=lambda x: x["id"])
        branch_ids = [topic_id] + [a["id"] for a in ancestors] + [d["id"] for d in descendants]
        return TopicBranch(
            topic_id=topic_id,
            topic_name=self.concept_label(topic_id),
            ancestors=ancestors,
            descendants=descendants,
            branch_ids=branch_ids,
        )

    def _index_questions(self) -> list[dict]:
        indexed = []
        for inst in self.kb.instances:
            if inst.instanceOf != "O_C_QUESTION":
                continue
            qid = str(_attr(inst, "name") or inst.id.replace("I_", "", 1))
            meta = Q_CODE.match(qid)
            type_a = self._first_assert(inst.id, REL_TYPE)
            diff_a = self._first_assert(inst.id, REL_DIFF)
            bloom_a = self._first_assert(inst.id, REL_BLOOM)
            ea_a = self._first_assert(inst.id, REL_EA)
            chapter_code = meta.group(1) if meta else ""
            concepts = []
            er_text = []
            ea_id = ea_a.target if ea_a else None
            if ea_id:
                for score_a in self.assertions_from.get(ea_id, []):
                    if score_a.relation != REL_SCORE:
                        continue
                    er = self.instance_map.get(score_a.target)
                    if er:
                        er_text.append(str(_attr(er, "name") or ""))
                        er_text.append(str(_attr(er, "missExplanation") or ""))
                    for req in self.assertions_from.get(score_a.target, []):
                        if req.relation == REL_CONCEPT and req.target:
                            concepts.append(req.target)
            ea_inst = self.instance_map.get(ea_id) if ea_id else None
            content = str(_attr(inst, "content") or "")
            ea_desc = str(_attr(ea_inst, "description") or "") if ea_inst else ""
            text = " ".join([qid, content, ea_desc, *er_text, *[self.concept_label(c) for c in concepts]])
            indexed.append({
                "inst": inst,
                "qid": qid,
                "content": content,
                "chapter_code": chapter_code,
                "chapter_id": self._chapter_id_from_code(chapter_code),
                "bloom_id": bloom_a.target if bloom_a else self._bloom_from_code(meta.group(2) if meta else ""),
                "type_id": type_a.target if type_a else self._type_from_code(meta.group(3) if meta else ""),
                "diff_id": diff_a.target if diff_a else self._diff_from_code(meta.group(4) if meta else ""),
                "ea_id": ea_id,
                "concepts": list(dict.fromkeys(concepts)),
                "tokens": _tokens(text),
            })
        return indexed

    def _chapter_id_from_code(self, code: str) -> str:
        for cid, prefix in CHAPTER_PREFIX.items():
            if prefix == code:
                return cid
        return ""

    def _bloom_from_code(self, code: str) -> str:
        return {"R": "O_C_BLOOM_LEVEL_R", "U": "O_C_BLOOM_LEVEL_U", "AP": "O_C_BLOOM_LEVEL_AP"}.get(code, "")

    def _type_from_code(self, code: str) -> str:
        return {
            "DES": "O_C_QUESTION_TYPE_DESCRIPTIVE",
            "PRO": "O_C_QUESTION_TYPE_PROCEDURE",
            "APP": "O_C_QUESTION_TYPE_APPLICATION",
        }.get(code, "")

    def _diff_from_code(self, code: str) -> str:
        return {
            "E": "O_C_DIFFICULTY_EASY",
            "M": "O_C_DIFFICULTY_MEDIUM",
            "H": "O_C_DIFFICULTY_HARD",
        }.get(code, "")

    def _first_assert(self, source: str, rel: str):
        for a in self.assertions_from.get(source, []):
            if a.relation == rel:
                return a
        return None

    def _passes_filters(self, q: dict, chapter_id, bloom_id, diff_id, type_id) -> bool:
        if chapter_id and q["chapter_id"] != chapter_id:
            return False
        if bloom_id and q["bloom_id"] != bloom_id:
            return False
        if diff_id and q["diff_id"] != diff_id:
            return False
        if type_id and q["type_id"] != type_id:
            return False
        return True

    def _concept_score(self, question_concepts: list[str], branch: TopicBranch) -> tuple[float, list[str]]:
        if not question_concepts:
            return 0.0, []
        topic = branch.topic_id
        ancestors = {a["id"] for a in branch.ancestors}
        descendants = {d["id"] for d in branch.descendants}
        matched = []
        best = 0.0
        for cid in question_concepts:
            if cid == topic:
                best = max(best, 1.0)
                matched.append(cid)
            elif cid in descendants:
                best = max(best, 0.88)
                matched.append(cid)
            elif cid in ancestors:
                best = max(best, 0.58)
                matched.append(cid)
        if not matched:
            return 0.0, []
        overlap = len(set(matched)) / max(len(set(question_concepts)), 1)
        return (0.85 * best) + (0.15 * overlap), matched

    def _text_score(self, q_tokens: set[str], branch: TopicBranch) -> float:
        topic_tokens = set()
        for cid in branch.branch_ids:
            topic_tokens |= _tokens(self.concept_text(cid))
        if not q_tokens or not topic_tokens:
            return 0.0
        inter = q_tokens & topic_tokens
        union = q_tokens | topic_tokens
        jaccard = len(inter) / max(len(union), 1)
        overlap = len(inter) / max(len(topic_tokens), 1)
        return (0.55 * jaccard) + (0.45 * overlap)

    def search(self, filters: QuestionFilter) -> RetrievalResult:
        chapter_id = self.resolve_chapter(filters.chapter)
        bloom_id = self.resolve_bloom(filters.bloom)
        diff_id = self.resolve_difficulty(filters.difficulty)
        type_id = self.resolve_question_type(filters.question_type)
        limit = max(1, int(filters.limit or 10))

        branch = None
        if filters.topic and str(filters.topic).strip():
            branch = self.topic_branch(filters.topic)

        applied = {
            "chapter": chapter_id,
            "bloom": bloom_id,
            "topic": branch.topic_id if branch else None,
            "difficulty": diff_id,
            "question_type": type_id,
            "limit": limit,
            "min_similarity": MIN_SIMILARITY if branch else None,
        }

        candidates = [q for q in self._questions if self._passes_filters(q, chapter_id, bloom_id, diff_id, type_id)]
        ranked: list[RankedQuestion] = []
        for q in candidates:
            if branch:
                c_score, matched = self._concept_score(q["concepts"], branch)
                t_score = self._text_score(q["tokens"], branch)
                score = (CONCEPT_W * c_score) + (TEXT_W * t_score)
            else:
                c_score, matched, t_score, score = 1.0, q["concepts"], 1.0, 1.0
            ranked.append(RankedQuestion(
                question_id=q["qid"],
                instance_id=q["inst"].id,
                content=q["content"],
                chapter=q["chapter_code"] or q["chapter_id"],
                bloom=q["bloom_id"],
                question_type=q["type_id"],
                difficulty=q["diff_id"],
                score=score,
                concept_score=c_score,
                text_score=t_score,
                matched_concepts=matched,
                expected_answer_id=q["ea_id"],
            ))

        ranked.sort(key=lambda x: (-x.score, x.question_id))
        if branch:
            ranked = [q for q in ranked if q.score >= MIN_SIMILARITY]
        return RetrievalResult(
            filters=applied,
            branch=branch,
            candidate_count=len(candidates),
            questions=ranked[:limit],
        )


def _default_ontology_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ontology")


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Loc cau hoi theo Chuong / Bloom / Topic / Do kho / Dang (tat ca tuy chon) va tra ve top 10 giong topic."
    )
    parser.add_argument("--chapter", default=None, help="C1 | 2 | O_C_CHAPTER_LINKED_LIST | ...")
    parser.add_argument("--bloom", default=None, help="remember | R | O_C_BLOOM_LEVEL_U | ...")
    parser.add_argument("--topic", default=None, help="O_C_LINEAR_SEARCH | linear search | ...")
    parser.add_argument("--difficulty", default=None, help="easy | E | medium | hard")
    parser.add_argument("--type", dest="question_type", default=None, help="descriptive | procedure | application")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--ontology", default=_default_ontology_dir())
    args = parser.parse_args(list(argv) if argv is not None else None)

    kb = DsaKbLoader(args.ontology).load_kb()
    engine = RetrievalEngine(kb)
    result = engine.search(QuestionFilter(
        chapter=args.chapter,
        bloom=args.bloom,
        topic=args.topic,
        difficulty=args.difficulty,
        question_type=args.question_type,
        limit=args.limit,
    ))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
