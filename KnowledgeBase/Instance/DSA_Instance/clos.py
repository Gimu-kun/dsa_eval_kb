from MetaModel import Instance
from Ontology.DSA_Ontology.Concepts.clos import CLO1, CLO2, CLO3, CLO4, CLO5

clo1 = Instance(
    id="I_CLO1",
    concept_id=CLO1.id,
    attributes={
        "weight": 1,
        "description": "Hiểu được các khái niệm cơ bản về thuật toán, độ phức tạp và phương pháp biểu diễn thuật toán"
    },
    relations={
        "linked": ["I_CHAPTER_OVERVIEW"]
    }
)

clo2 = Instance(
    id="I_CLO2",
    concept_id=CLO2.id,
    attributes={
        "weight": 2,
        "description": "Phân tích bài toán tìm kiếm, xác định ràng buộc và đánh giá các giải pháp thuật toán phù hợp"
    },
    relations={
        "linked": ["I_CHAPTER_SEARCHING_AND_SORTING"]
    }
)

clo3 = Instance(
    id="I_CLO3",
    concept_id=CLO3.id,
    attributes={
        "weight": 3,
        "description": "Phân tích bài toán sắp xếp, xác định ràng buộc và đánh giá giải pháp sắp xếp hiệu quả"
    },
    relations={
        "linked": ["I_CHAPTER_SEARCHING_AND_SORTING"]
    }
)

clo4 = Instance(
    id="I_CLO4",
    concept_id=CLO4.id,
    attributes={
        "weight": 4,
        "description": "Mô tả và phân tích các cấu trúc dữ liệu cơ bản"
    },
    relations={
        "linked": ["I_CHAPTER_LINKLIST"]
    }
)

clo5 = Instance(
    id="I_CLO5",
    concept_id=CLO5.id,
    attributes={
        "weight": 5,
        "description": "Thiết kế và mô tả giải pháp sử dụng cấu trúc dữ liệu và thuật toán để giải quyết các bài toán đơn giản"
    },
    relations={
        "linked": ["I_CHAPTER_LINKLIST"]
    }
)