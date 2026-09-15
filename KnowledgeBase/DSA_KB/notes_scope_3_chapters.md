# Đề xuất bổ sung dữ liệu KB cho 3 chương DSA

Tài liệu rà soát tầng dữ liệu hiện có (`ontology/instances.json`, `ontology/assertions.json`) đối chiếu với phạm vi:

- **Chương 1** — Tổng quan CTDL & GT
- **Chương 2** — Tìm kiếm và sắp xếp
- **Chương 3** — Danh sách liên kết

Mục tiêu: chỉ ra phần đã đủ, phần còn thiếu, phần đang lấn chương khác, và đề xuất dữ liệu cần thêm **đúng mô hình hiện tại**.

---

## 1. Nguyên tắc mô hình (bắt buộc khi bổ sung)

Ontology hiện tại tách rõ:

| Tầng | File chính | Vai trò |
| --- | --- | --- |
| T-Box | `concepts.json`, `hierarchy.json`, `relations.json` | Khái niệm, phân cấp, quan hệ |
| A-Box | `instances.json`, `assertions.json` | Đối tượng cụ thể và liên kết giữa chúng |
| Ràng buộc | `rules.json`, `functions.json`, `operands.json` | Luật suy diễn / kiểm tra |

**Thuộc tính khái niệm chỉ chứa kiểu nguyên thủy** (`str`, `int`, `float`, `bool`). Mọi liên kết “giá trị là một khái niệm/instance khác” phải đi qua **relation + assertion**, không nhét reference vào attribute.

Đúng:

```json
{
  "id": "I_BINARY_SEARCH",
  "instanceOf": "O_C_BINARY_SEARCH",
  "attributes": [
    { "name": "name", "value": "binary search" },
    { "name": "isValid", "value": true }
  ]
}
```

```json
{
  "source": "I_BINARY_SEARCH",
  "relation": "REL_ALGORITHM_HAS_WORST_COMPLEXITY",
  "target": "I_LOGARITHMIC_TIME"
}
```

Sai (không làm):

```json
{
  "name": "worstComplexity",
  "value": "O_C_LOGARITHMIC_TIME"
}
```

Quan hệ đã có sẵn và **nên tận dụng trước khi thêm schema mới**:

- `hasTopic`, `contributesTo`
- `hasCharacteristic`, `requiresIdentify`
- `evaluates`, `measures`, `quantifies`
- `hasComplexity`, `hasNotation`, `betterThan`
- `hasBestComplexity` / `hasAverageComplexity` / `hasWorstComplexity`
- `usesTechnique`, `operatesOn`, `applyTo`
- `hasHead`, `hasTail`, `hasPrev`, `hasNext`, `hasData`, `pointTo`

`KnowledgeBase/DSA_KB/data/instances.json` và `data/assertions.json` đang rỗng. Dữ liệu thật đang nằm trong `ontology/`. Khi bổ sung, ghi vào `ontology/` cho thống nhất với hiện trạng, hoặc chuyển hết A-Box sang `data/` rồi để `ontology/` chỉ còn T-Box.

---

## 2. Phạm vi 3 chương (chuẩn đối chiếu)

Phạm vi lấy từ mô tả instance chương + CLO hiện có, **không mở rộng** sang Stack, Queue, Cây, Đồ thị, Bảng băm.

### Chương 1 — Tổng quan CTDL & GT (CLO1)

- Chương trình = thuật toán + dữ liệu
- Dữ liệu, kiểu dữ liệu, cấu trúc dữ liệu
- Phân loại: nguyên thủy / không nguyên thủy; truy cập trực tiếp / tuần tự
- Mảng 1 chiều, mảng 2 chiều (ở mức khái niệm, chưa phải ADT Stack/Queue)
- Thuật toán và 5 đặc trưng: xác định, hữu hạn, đúng đắn, hiệu quả, khả thi
- Input / Output
- Biểu diễn thuật toán (mã giả, lưu đồ, ngôn ngữ tự nhiên) — **CLO1 nêu rõ nhưng ontology chưa có**
- Phân tích lý thuyết / thực nghiệm
- Độ phức tạp thời gian, không gian; Big-O
- Giới thiệu phương pháp thiết kế (chỉ ở mức tên: vét cạn, chia để trị, đệ quy, …)

### Chương 2 — Tìm kiếm & sắp xếp (CLO2, CLO3)

Mô tả `I_CHAPTER_SEARCHING_AND_SORTING` chỉ nêu **lõi**:

- Tìm kiếm tuyến tính, tìm kiếm nhị phân
- Sắp xếp nổi bọt, chọn, chèn
- Độ phức tạp best / average / worst của các thuật toán trên

Quick / Merge / Heap / Bucket / Radix đã có trong T-Box và A-Box nhưng **không nằm trong mô tả chương 2**. Xem mục 5.

### Chương 3 — Danh sách liên kết (CLO4, CLO5)

- Node, con trỏ
- DSLK đơn, đôi, vòng
- Thao tác: duyệt, tìm, chèn, xóa
- So sánh mảng và DSLK (phù hợp CLO5 ở mức đơn giản)

Không đi vào cài Stack/Queue bằng DSLK, skip list, hay cây.

---

## 3. Hiện trạng dữ liệu

| Thành phần | Số lượng | Ghi chú |
| --- | ---: | --- |
| Concept | 89 | Schema khá đủ cho 3 chương, trừ biểu diễn thuật toán |
| Hierarchy | 79 | Ổn |
| Relation | 29 | Đủ dùng nếu A-Box được điền |
| Instance | 62 | Nhiều concept trong phạm vi **chưa có instance** |
| Assertion | 66 | Tập trung Big-O của sort/search; DSLK gần như trống |
| Rule / Function | 3 / 1 | Phục vụ đánh giá + kiểm tra đặc trưng thuật toán |
| `concept.operation` | 0 | Mọi concept đều `"operation": []` |
| `concept.invariant` | 0 | Trống |

### 3.1 Concept đã có instance

Assessment: Bloom, Difficulty, Rubric, Question Type, CLO, Chapter.

DSA đã instantiate: Program, Algorithm (generic), Problem solving, 5 đặc trưng, Input/Output, Analysis (generic + theoretical + experimental), 6 kỹ thuật thiết kế, Complexity / Time / Space, Resource / Execution time / Memory, 7 lớp Big-O, Data (generic), Linked list (generic), Linear/Binary search, Selection/Bubble/Insertion/Quick/Merge/Heap/Bucket/Radix sort.

### 3.2 Concept trong phạm vi 3 chương nhưng **chưa có instance**

| Concept | Chương | Mức thiếu |
| --- | --- | --- |
| `O_C_DATA_STRUCTURE` | 1 | Cao |
| `O_C_PRIMITIVE_DATA_STRUCTURE` | 1 | Cao |
| `O_C_INTEGER`, `O_C_FLOAT`, `O_C_BOOLEAN`, `O_C_CHARACTER` | 1 | Cao |
| `O_C_NON_PRIMITIVE_DATA_STRUCTURE` | 1 | Cao |
| `O_C_DIRECT_ACCESS_DATA_STRUCTURE` | 1 | Cao |
| `O_C_ARRAY`, `O_C_1D_ARRAY`, `O_C_2D_ARRAY` | 1 | Cao |
| `O_C_SEQUENTIAL_ACCESS_DATA_STRUCTURE` | 1 | Cao |
| `O_C_SEARCHING_ALGORITHM`, `O_C_SORTING_ALGORITHM` | 2 | Cao |
| `O_C_COMPARISON_BASED_SORTING_ALGORITHM` | 2 | Trung bình |
| `O_C_NON_COMPARISON_BASED_SORTING_ALGORITHM` | 2 | Thấp (ngoài lõi chương) |
| `O_C_SINGLY_LINKED_LIST` | 3 | Cao |
| `O_C_DOUBLY_LINKED_LIST` | 3 | Cao |
| `O_C_CIRCULAR_LINKED_LIST` | 3 | Cao |
| `O_C_NODE` | 3 | Cao |
| `O_C_POINTER` | 3 | Cao |

### 3.3 Relation đã định nghĩa nhưng **chưa có assertion** (trong phạm vi DSA)

- `REL_ALGORITHM_USES_TECHNIQUE` — không thuật toán nào gắn kỹ thuật
- `REL_ALGORITHM_OPERATES_ON_DATA` — chỉ có `I_ALGORITHM → I_DATA` (quá generic)
- Toàn bộ quan hệ DSLK: `hasHead`, `hasTail`, `hasPrev`, `hasNext`, `hasData`, `pointTo`
- `I_THEORETICAL_ANALYSIS`, `I_EXPERIMENTAL_ANALYSIS`, `I_TIME_COMPLEXITY`, `I_SPACE_COMPLEXITY` không được nối vào mạng phân tích

### 3.4 Lỗi dữ liệu cần sửa trước khi bổ sung

1. `hasTopic` của Chương 2 đang trỏ **ID concept**, không phải **ID instance**:

```json
{ "source": "I_CHAPTER_SEARCHING_AND_SORTING", "relation": "REL_CHAPTER_HAS_TOPIC", "target": "O_C_SEARCHING_ALGORITHM" }
{ "source": "I_CHAPTER_SEARCHING_AND_SORTING", "relation": "REL_CHAPTER_HAS_TOPIC", "target": "O_C_SORTING_ALGORITHM" }
```

Sửa thành instance (sau khi tạo), ví dụ `I_SEARCHING_ALGORITHM`, `I_LINEAR_SEARCH`, …

2. Bucket sort worst-case ghi `O(n)` — thực tế worst-case phổ biến là `O(n²)` khi phân bố lệch.
3. Radix sort ghi `O(n)` cho cả 3 trường hợp — nên là `O(d(n+k))`; nếu không mô hình `d,k` thì ít nhất ghi chú hạn chế, không khẳng định `O(n)` tuyệt đối.
4. `I_CHAPTER_LINKED_LIST.title` = `"link list"` (typo).
5. Instance thuật toán cụ thể (linear search, bubble sort, …) **không có** attribute `isValid` dù `O_C_ALGORITHM` định nghĩa field này.

---

## 4. Kết luận bao phủ

**Chưa đủ.** Schema T-Box phủ khá tốt khung 3 chương, nhưng A-Box mới ở mức “khung sườn”:

| Chương | Schema | Dữ liệu instance/assertion | Đánh giá |
| --- | --- | --- | --- |
| 1 Tổng quan | ~80% | ~40% | Có thuật toán/đặc trưng/Big-O; **thiếu gần hết CTDL nguyên thủy + mảng**; thiếu biểu diễn thuật toán |
| 2 TK & SX | ~90% lõi, thừa phần nâng cao | ~55% lõi | Đã có best/avg/worst **thời gian** cho 8 thuật toán; thiếu kỹ thuật, cấu trúc dữ liệu thao tác, độ phức tạp không gian, tính ổn định |
| 3 DSLK | ~70% | ~10% | Chỉ có 1 instance `I_LINKED_LIST` và 1 `hasTopic`; **không có node, pointer, 3 biến thể, thao tác** |

Phần Assessment (Exam, Question, Expected Answer) **chưa có instance** — không chặn việc phủ kiến thức 3 chương, nên tách sang pha đề thi, không nhồi vào đợt này.

---

## 5. Phần đang lấn chương khác — giữ nhẹ, không đào sâu

Giữ concept/instance **tên** nếu đã có, nhưng **không** thêm thao tác, bất biến, hay ví dụ chi tiết.

| Mục | Lý do | Việc nên làm |
| --- | --- | --- |
| `O_C_STACK`, `O_C_QUEUE`, `O_C_TREE` | Chương sau | **Không tạo instance**, không `hasTopic` |
| `I_HEAP_SORT` | Cần Heap/Cây | Có thể giữ instance + Big-O; **không** `hasTopic` Chương 2; không `operatesOn` Tree |
| `I_QUICK_SORT`, `I_MERGE_SORT` | Nhiều giáo trình để chương sắp xếp nâng cao | Tùy đề cương: nếu Chương 2 chỉ 3 sort cơ bản thì **không** `hasTopic` Chương 2 |
| `I_BUCKET_SORT`, `I_RADIX_SORT` | Ngoài mô tả chương | Giữ nhẹ hoặc gỡ khỏi `hasTopic` |
| `I_DYNAMIC_PROGRAMMING`, `I_GREEDY`, `I_BACKTRACKING` | Chương 1 chỉ giới thiệu tên | Giữ instance; **không** tạo bài toán/thuật toán cụ thể |
| Graph, Hash, AVL, Huffman, … | Ngoài 3 chương | **Không thêm** |

Gợi ý `hasTopic` Chương 2 (lõi):

- `I_SEARCHING_ALGORITHM`, `I_LINEAR_SEARCH`, `I_BINARY_SEARCH`
- `I_SORTING_ALGORITHM`, `I_COMPARISON_BASED_SORTING_ALGORITHM`
- `I_BUBBLE_SORT`, `I_SELECTION_SORT`, `I_INSERTION_SORT`
- `I_TIME_COMPLEXITY`, `I_SPACE_COMPLEXITY` (đánh giá độ phức tạp của TK/SX)

Quick/Merge chỉ gắn `hasTopic` nếu đề cương chính thức dạy trong Chương 2.

---

## 6. Đề xuất bổ sung — ưu tiên P0 (bắt buộc để phủ 3 chương)

Toàn bộ dưới đây dùng **concept/relation đã có**, attribute nguyên thủy.

### 6.1 Instances thiếu (P0)

#### Chương 1

```text
I_DATA_STRUCTURE
I_PRIMITIVE_DATA_STRUCTURE          notation: ví dụ "built-in"
I_INTEGER                           notation: "int"
I_FLOAT                             notation: "float"
I_BOOLEAN                           notation: "bool"
I_CHARACTER                         notation: "char"
I_NON_PRIMITIVE_DATA_STRUCTURE
I_DIRECT_ACCESS_DATA_STRUCTURE
I_SEQUENTIAL_ACCESS_DATA_STRUCTURE
I_ARRAY
I_1D_ARRAY
I_2D_ARRAY
```

Attribute chỉ `name` (+ `notation` với kiểu nguyên thủy). Không đặt `elementType = Integer` vào attribute — mối liên hệ kiểu phần tử, nếu cần, thêm relation riêng (P2).

Điền thêm `rank` (int) cho 7 instance Big-O: 1=`O(1)` … 7=`O(n!)` — đây là giá trị nguyên thủy, bổ sung cho `betterThan`.

#### Chương 2

```text
I_SEARCHING_ALGORITHM
I_SORTING_ALGORITHM
I_COMPARISON_BASED_SORTING_ALGORITHM
```

`I_NON_COMPARISON_BASED_SORTING_ALGORITHM` chỉ tạo nếu vẫn giữ Bucket/Radix trong phạm vi.

Bổ sung `isValid: true` cho các instance thuật toán lõi.

#### Chương 3

```text
I_SINGLY_LINKED_LIST
I_DOUBLY_LINKED_LIST
I_CIRCULAR_LINKED_LIST
I_NODE
I_POINTER                     # con trỏ generic
I_HEAD_POINTER
I_TAIL_POINTER
I_NEXT_POINTER
I_PREV_POINTER
```

`I_HEAD_POINTER` … `instanceOf` `O_C_POINTER`, phân biệt vai trò bằng assertion (`hasHead`, `hasNext`, …), không bằng attribute kiểu concept.

### 6.2 Assertions thiếu (P0)

#### Chương 1 — chủ đề và phân tích

```text
I_CHAPTER_OVERVIEW  hasTopic  I_PROGRAM
I_CHAPTER_OVERVIEW  hasTopic  I_DATA_STRUCTURE
I_CHAPTER_OVERVIEW  hasTopic  I_PRIMITIVE_DATA_STRUCTURE
I_CHAPTER_OVERVIEW  hasTopic  I_NON_PRIMITIVE_DATA_STRUCTURE
I_CHAPTER_OVERVIEW  hasTopic  I_ARRAY
I_CHAPTER_OVERVIEW  hasTopic  I_1D_ARRAY
I_CHAPTER_OVERVIEW  hasTopic  I_2D_ARRAY
I_CHAPTER_OVERVIEW  hasTopic  I_TIME_COMPLEXITY
I_CHAPTER_OVERVIEW  hasTopic  I_SPACE_COMPLEXITY
I_CHAPTER_OVERVIEW  hasTopic  I_THEORETICAL_ANALYSIS
I_CHAPTER_OVERVIEW  hasTopic  I_EXPERIMENTAL_ANALYSIS
I_CHAPTER_OVERVIEW  hasTopic  I_DIVIDE_AND_CONQUER
I_CHAPTER_OVERVIEW  hasTopic  I_BRUTE_FORCE
I_CHAPTER_OVERVIEW  hasTopic  I_RECURSIVE
```

Không `hasTopic` Stack/Queue/Tree.

Nối tầng phân tích (relation đã có):

```text
I_THEORETICAL_ANALYSIS   evaluates    I_ALGORITHM
I_THEORETICAL_ANALYSIS   measures     I_TIME_COMPLEXITY
I_THEORETICAL_ANALYSIS   measures     I_SPACE_COMPLEXITY
I_EXPERIMENTAL_ANALYSIS  evaluates    I_ALGORITHM
I_EXPERIMENTAL_ANALYSIS  quantifies   I_EXECUTION_TIME
I_EXPERIMENTAL_ANALYSIS  quantifies   I_MEMORY_USAGE
I_TIME_COMPLEXITY        hasNotation  I_CONSTANT_TIME
I_TIME_COMPLEXITY        hasNotation  I_LOGARITHMIC_TIME
I_TIME_COMPLEXITY        hasNotation  I_LINEAR_TIME
I_TIME_COMPLEXITY        hasNotation  I_LINEARITHMIC_TIME
I_TIME_COMPLEXITY        hasNotation  I_QUADRATIC_TIME
I_TIME_COMPLEXITY        hasNotation  I_EXPONENTIAL_TIME
I_TIME_COMPLEXITY        hasNotation  I_FACTORIAL_TIME
I_SPACE_COMPLEXITY       hasNotation  I_CONSTANT_TIME
I_SPACE_COMPLEXITY       hasNotation  I_LINEAR_TIME
```

CLO (tuỳ chọn, không bắt buộc): Chương 1 cũng có thể `contributesTo` CLO4 vì mảng/CTDL nguyên thủy là CTDL cơ bản. Hiện CLO4 đang chỉ gắn Chương 3.

#### Chương 2 — sửa hasTopic + gắn kỹ thuật, dữ liệu, độ phức tạp không gian

```text
# thay 2 assertion sai ID
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_SEARCHING_ALGORITHM
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_SORTING_ALGORITHM
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_LINEAR_SEARCH
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_BINARY_SEARCH
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_BUBBLE_SORT
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_SELECTION_SORT
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_INSERTION_SORT
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_TIME_COMPLEXITY
I_CHAPTER_SEARCHING_AND_SORTING  hasTopic  I_SPACE_COMPLEXITY
```

`usesTechnique` / `operatesOn` (lõi):

| Algorithm | usesTechnique | operatesOn |
| --- | --- | --- |
| Linear search | Brute force | 1D Array |
| Binary search | Divide and conquer | 1D Array |
| Selection sort | Brute force | 1D Array |
| Bubble sort | Brute force | 1D Array |
| Insertion sort | Brute force | 1D Array |

Nếu giữ Quick/Merge: `usesTechnique` Divide and conquer, `operatesOn` 1D Array — **không** `hasTopic` trừ khi đề cương yêu cầu.

Độ phức tạp **không gian** (dùng `hasComplexity` → instance space, rồi `hasNotation` → Big-O), **không** nhét `O(1)` vào attribute:

```text
I_LINEAR_SEARCH_SPACE     instanceOf  O_C_SPACE_COMPLEXITY   name: "linear search space"
I_BINARY_SEARCH_SPACE     instanceOf  O_C_SPACE_COMPLEXITY
I_BUBBLE_SORT_SPACE       instanceOf  O_C_SPACE_COMPLEXITY
I_SELECTION_SORT_SPACE    instanceOf  O_C_SPACE_COMPLEXITY
I_INSERTION_SORT_SPACE    instanceOf  O_C_SPACE_COMPLEXITY

I_LINEAR_SEARCH   hasComplexity  I_LINEAR_SEARCH_SPACE
I_LINEAR_SEARCH_SPACE  hasNotation  I_CONSTANT_TIME
# binary / bubble / selection / insertion: tương tự → O(1)
# (phiên bản đệ quy binary search có thể O(log n); với CTDL mảng lặp, O(1) là đủ cho chương)
```

Best/avg/worst **thời gian** của 5 thuật toán lõi đã có — giữ nguyên.

#### Chương 3 — cấu trúc + chủ đề

```text
I_CHAPTER_LINKED_LIST  hasTopic  I_SINGLY_LINKED_LIST
I_CHAPTER_LINKED_LIST  hasTopic  I_DOUBLY_LINKED_LIST
I_CHAPTER_LINKED_LIST  hasTopic  I_CIRCULAR_LINKED_LIST
I_CHAPTER_LINKED_LIST  hasTopic  I_NODE
I_CHAPTER_LINKED_LIST  hasTopic  I_POINTER
I_CHAPTER_LINKED_LIST  hasTopic  I_ARRAY          # để so sánh CTDL
```

Quan hệ cấu trúc (schema đã có, A-Box đang trống):

```text
I_SINGLY_LINKED_LIST   hasHead   I_HEAD_POINTER
I_SINGLY_LINKED_LIST   hasTail   I_TAIL_POINTER      # optional, nhiều giáo trình SLL chỉ nhấn head
I_NODE                 hasNext   I_NEXT_POINTER
I_NODE                 hasData   I_DATA              # hoặc I_INTEGER nếu muốn cụ thể kiểu phần tử
I_HEAD_POINTER         pointTo   I_NODE
I_NEXT_POINTER         pointTo   I_NODE

I_DOUBLY_LINKED_LIST   hasHead   I_HEAD_POINTER
I_DOUBLY_LINKED_LIST   hasTail   I_TAIL_POINTER
I_NODE                 hasPrev   I_PREV_POINTER
```

Lưu ý: `I_NODE` dùng chung cho 3 loại list là đúng T-Box. Nếu cần phân biệt node đôi (có prev) với node đơn (không prev), tạo thêm instance `I_SLL_NODE`, `I_DLL_NODE` cùng `instanceOf O_C_NODE`, rồi chỉ `hasPrev` trên node đôi — **vẫn là data, không cần concept mới**.

### 6.3 Thao tác DSLK và mảng — instance thuật toán, không nhét concept vào attribute (P0)

Mọi concept đang `"operation": []`. Để phủ “chèn / xóa / duyệt” mà **không phá nguyên tắc attribute nguyên thủy**, mô hình thao tác như **algorithm instance** `operatesOn` CTDL.

Chương 1 (mảng, độ phức tạp điển hình):

| Instance | operatesOn | worst | best |
| --- | --- | --- | --- |
| `I_ARRAY_ACCESS` | 1D Array | O(1) | O(1) |
| `I_ARRAY_INSERT` | 1D Array | O(n) | O(1) (cuối mảng, còn chỗ) |
| `I_ARRAY_DELETE` | 1D Array | O(n) | O(1) |
| `I_ARRAY_TRAVERSE` | 1D Array | O(n) | O(n) |

Chương 3 (DSLK đơn — lõi; đôi/vòng làm tương tự nếu cần đủ CLO4):

| Instance | operatesOn | worst |
| --- | --- | --- |
| `I_SLL_TRAVERSE` | Singly linked list | O(n) |
| `I_SLL_SEARCH` | Singly linked list | O(n) |
| `I_SLL_INSERT_HEAD` | Singly linked list | O(1) |
| `I_SLL_INSERT_TAIL` | Singly linked list | O(n) nếu không tail; O(1) nếu có tail |
| `I_SLL_INSERT_AT` | Singly linked list | O(n) |
| `I_SLL_DELETE_HEAD` | Singly linked list | O(1) |
| `I_SLL_DELETE_AT` | Singly linked list | O(n) |

Gắn `hasTopic` Chương 3 tới các instance thao tác trên. `usesTechnique` = Brute force.

Ví dụ instance:

```json
{
  "id": "I_SLL_INSERT_HEAD",
  "instanceOf": "O_C_ALGORITHM",
  "attributes": [
    { "name": "name", "value": "singly linked list insert head" },
    { "name": "isValid", "value": true }
  ]
}
```

```json
{ "source": "I_SLL_INSERT_HEAD", "relation": "REL_ALGORITHM_OPERATES_ON_DATA", "target": "I_SINGLY_LINKED_LIST" }
{ "source": "I_SLL_INSERT_HEAD", "relation": "REL_ALGORITHM_HAS_BEST_COMPLEXITY", "target": "I_CONSTANT_TIME" }
{ "source": "I_SLL_INSERT_HEAD", "relation": "REL_ALGORITHM_HAS_WORST_COMPLEXITY", "target": "I_CONSTANT_TIME" }
{ "source": "I_SLL_INSERT_HEAD", "relation": "REL_ALGORITHM_USES_TECHNIQUE", "target": "I_BRUTE_FORCE" }
{ "source": "I_CHAPTER_LINKED_LIST", "relation": "REL_CHAPTER_HAS_TOPIC", "target": "I_SLL_INSERT_HEAD" }
```

Không tạo attribute `operationType = O_C_...`.

---

## 7. Đề xuất P1 — lỗ hổng kiến thức cần schema rất mỏng

Chỉ thêm concept/relation khi **không thể** diễn tả bằng instance + relation hiện có. Attribute mới phải là nguyên thủy.

### 7.1 Biểu diễn thuật toán (CLO1 — đang thiếu hoàn toàn)

Thêm concept:

```text
O_C_ALGORITHM_REPRESENTATION     domain: DSA
  attributes: name:str, description:str?

O_C_PSEUDOCODE          subclassOf  O_C_ALGORITHM_REPRESENTATION
O_C_FLOWCHART           subclassOf  O_C_ALGORITHM_REPRESENTATION
O_C_NATURAL_LANGUAGE    subclassOf  O_C_ALGORITHM_REPRESENTATION
```

Relation:

```text
REL_ALGORITHM_REPRESENTED_BY
  source: O_C_ALGORITHM
  target: O_C_ALGORITHM_REPRESENTATION
  cardinality: (0..*)
```

Instance: `I_PSEUDOCODE`, `I_FLOWCHART`, `I_NATURAL_LANGUAGE`.

Assertion: `I_CHAPTER_OVERVIEW hasTopic` cả ba; `I_ALGORITHM representedBy` cả ba (mức tổng quan).

Không nhồi nội dung mã giả cụ thể vào attribute kiểu concept.

### 7.2 Tính ổn định / in-place của sắp xếp (CLO3)

Đây là **bool nguyên thủy** — thêm vào `O_C_SORTING_ALGORITHM` (không phải search):

```text
isStable: bool, required false
isInPlace: bool, required false
```

Giá trị đề xuất:

| Instance | isStable | isInPlace |
| --- | --- | --- |
| Bubble sort | true | true |
| Insertion sort | true | true |
| Selection sort | false | true |
| Merge sort (nếu giữ) | true | false |
| Quick sort (nếu giữ) | false | true |
| Heap sort (nếu giữ) | false | true |

Không tạo concept `O_C_STABLE_SORT`.

### 7.3 Tiền điều kiện tìm kiếm nhị phân

Binary search yêu cầu mảng đã sắp. Có 2 cách đúng mô hình:

1. **Ưu tiên, không thêm schema:** invariant trên `O_C_BINARY_SEARCH` (condition so sánh, không chứa reference concept trong attribute).
2. Hoặc relation mới `requiresSortedCollection` → `O_C_1D_ARRAY` với attribute relation `mustBeSorted: bool = true` (bool là nguyên thủy trên **relation**, giống `weight` của rubric).

Không viết `"precondition": "O_C_SORTING_ALGORITHM"` trong attribute concept.

### 7.4 `concept.operation` (tuỳ chọn, song song P0)

Meta-model đã có `Operation` với `Parameter.value_type` là chuỗi. Có thể điền chữ ký thao tác trên `O_C_ARRAY` và `O_C_LINKED_LIST` (`insert`, `delete`, `traverse`, `search`, `access`) với input/output kiểu nguyên thủy hoặc tên tham số (`index:int`, `value:str`). Đây là T-Box, không thay assertion P0 — chỉ giúp UI/engine biết chữ ký.

---

## 8. Đề xuất P2 — làm giàu, không chặn bao phủ

- Ví dụ A-Box cụ thể một SLL 3 node (`I_NODE_A/B/C` + pointer) để minh họa `pointTo` / `hasNext` — hữu ích cho câu hỏi thủ tục Chương 3.
- `applyTo`: `I_LINEAR_SEARCH` / `I_BINARY_SEARCH` → bài toán tìm kiếm; 3 sort → bài toán sắp xếp. Hiện cardinality `(0..1)` nên chỉ cần 2 instance `I_PROBLEM_SEARCHING`, `I_PROBLEM_SORTING` (tách `I_PROBLEM_SOLVING` generic).
- Chương 1 `contributesTo` CLO4 (mảng).
- Sửa Big-O Bucket/Radix nếu vẫn giữ các instance này.
- Không instantiate Exam/Question ở pha này.

---

## 9. Những gì **không** nên bổ sung

- Attribute concept có `value_type: concept` / `reference` (enum có sẵn nhưng trái nguyên tắc đã chốt).
- Concept Stack/Queue/Tree instance, thao tác push/pop/enqueue, duyệt cây.
- Bài toán QHĐ, greedy, backtracking cụ thể.
- Counting sort, interpolation search, sentinel search (không có trong T-Box và ngoài mô tả chương).
- Circular doubly linked list (lấn quá Chương 3 cơ bản).
- Cài đặt DSLK bằng mảng / XOR list / skip list.
- Nhồi đề thi (Exam, Question, Expected Answer) vào đợt phủ kiến thức.

---

## 10. Thứ tự triển khai gợi ý

1. **Sửa lỗi A-Box hiện có** (hasTopic Chương 2, typo title, `isValid`, cân nhắc gỡ Heap/Bucket/Radix khỏi phạm vi chương).
2. **P0 instances** CTDL Chương 1 + 3 biến thể DSLK + Node/Pointer + Searching/Sorting parent.
3. **P0 assertions** `hasTopic`, `usesTechnique`, `operatesOn`, mạng analysis, quan hệ DSLK.
4. **P0 algorithm instances** cho thao tác mảng và SLL.
5. **P1** concept biểu diễn thuật toán + `isStable` / `isInPlace`.
6. **P2** ví dụ 3-node, bài toán applyTo, invariant binary search.

Sau bước 4, 3 chương đã **đủ khung tri thức** để sinh câu hỏi mức Remember / Understand / Apply đúng CLO1–CLO5 mà không tràn Stack–Cây.

---

## 11. Checklist nhanh khi review dữ liệu mới

- [ ] Attribute instance chỉ `str` / `int` / `float` / `bool` / `null`
- [ ] Mọi liên kết concept↔concept đều là assertion, `source`/`target` là **ID instance** (`I_...`), không phải `O_C_...`
- [ ] Không `hasTopic` tới Stack, Queue, Tree
- [ ] Chương 2 lõi chỉ Linear, Binary, Bubble, Selection, Insertion (cộng complexity)
- [ ] Chương 3 có đủ Singly / Doubly / Circular + Node + Pointer + thao tác insert/delete/traverse
- [ ] Không thêm field kiểu `head`, `next`, `bestComplexity` vào attributes của concept
