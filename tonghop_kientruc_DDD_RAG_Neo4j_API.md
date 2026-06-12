# TỔNG HỢP: KIẾN TRÚC, DDD/RAG/KB/NEO4J, MODEL AI & GIAO TIẾP GIỮA CÁC SERVICE

> File tổng hợp từ Chương 1-4 (tieuluan_chuong1-4.md) của dự án **EcomAI** (`ecom-final/`).

---

## 1. Kiến trúc Monolithic và Microservices

### 1.1 Monolithic Architecture là gì?

**Monolithic** (kiến trúc nguyên khối) là mô hình mà toàn bộ ứng dụng — Presentation Layer, Business Logic Layer, Data Access Layer — được đóng gói thành **một đơn vị duy nhất**, chạy trong **một tiến trình**, dùng **chung một database**.

```
+----------------------------------------------------------+
|              MONOLITHIC APPLICATION                      |
|  Presentation Layer (UI / REST Controller)              |
|  Business Logic: ProductModule|UserModule|OrderModule.. |
|  Data Access Layer (ORM / DAO)                           |
|  Single Shared Database (MySQL / PostgreSQL)             |
+----------------------------------------------------------+
```

**Nhược điểm chính**: coupling cao, không scale riêng từng module, deploy rủi ro cao (1 module lỗi → cả hệ thống down), tech lock-in (1 ngôn ngữ/framework), khó onboard, test chậm, single point of failure.

**Khi nào nên dùng**: MVP, team nhỏ (<10 người), hệ thống đơn giản, giai đoạn đầu startup.

### 1.2 Microservices Architecture là gì?

**Microservices** là kiến trúc phân tách hệ thống thành các **service nhỏ, độc lập**, mỗi service:
- Thực hiện **một chức năng nghiệp vụ duy nhất**
- Có **database riêng** (Database-per-Service)
- Giao tiếp qua **REST API**
- Có thể **deploy độc lập**

So sánh nhanh:

| Tiêu chí | Monolithic | Microservices |
|---|---|---|
| Triển khai | 1 lần, toàn bộ | Từng service độc lập |
| Database | Dùng chung | Database-per-Service |
| Coupling | Cao | Thấp |
| Ngôn ngữ | 1 stack | Polyglot |
| Fault Isolation | Lỗi 1 = sập toàn hệ | Lỗi 1 service, phần còn lại vẫn chạy |
| Complexity vận hành | Đơn giản | Cao (cần DevOps, API Gateway, service discovery) |

Các Big Tech (Netflix, Amazon, Uber, Shopify) đều chuyển từ Monolithic → Microservices khi quy mô và team lớn lên. Bài học: Microservices không phải "silver bullet" — cần DDD để xác định đúng ranh giới service.

### 1.3 Áp dụng trong dự án EcomAI

Hệ thống được xây dựng theo **Microservices hoàn chỉnh**: **6 microservices Django + 1 AI Service FastAPI + 1 Frontend**, đứng sau **1 API Gateway (Nginx)**, dùng **6 database riêng** (1 MySQL + 5 PostgreSQL) + Redis (cache) + Neo4j (Knowledge Graph).

```
                    INTERNET / BROWSER
                          |
                 +--------v--------+
                 |   API Gateway   |
                 |  Nginx :80      |
                 +--------+--------+
                          |
  +------+ +-------+ +------+ +-------+ +---------+ +---------+
  | User | |Product| | Cart | | Order | | Payment | |Shipping |
  |:8000 | |:8001  | |:8002 | |:8003  | | :8004   | | :8005   |
  |MySQL | |Postgre| |Postg.| |Postg. | | Postg.  | | Postg.  |
  +------+ +---+---+ +------+ +-------+ +---------+ +---------+
               |
               | (volume mount user_behavior_log.csv)
               v
       +----------------+      +--------+
       |  AI Service    |<---->| Neo4j  |
       |  FastAPI :8006 |      |KB_Graph|
       +----------------+      +--------+
```

| Service | Port | DB | Vai trò |
|---|---|---|---|
| user-service | 8000 | MySQL | Auth, JWT, RBAC |
| product-service | 8001 | PostgreSQL | Sản phẩm, danh mục, behavior log |
| cart-service | 8002 | PostgreSQL | Giỏ hàng |
| order-service | 8003 | PostgreSQL | Đơn hàng |
| payment-service | 8004 | PostgreSQL | Thanh toán (mock COD/MoMo/VNPay) |
| shipping-service | 8005 | PostgreSQL | Vận chuyển |
| ai-service | 8006 | — (Neo4j) | Gợi ý + Chatbot |

Mỗi service Django chỉ truy cập DB của chính nó, **không bao giờ truy cập trực tiếp DB của service khác** — mọi giao tiếp đi qua REST API.

---

## 2. DDD, RAG, Knowledgebase (KB_Graph) và Neo4j

### 2.1 Domain-Driven Design (DDD) là gì?

**DDD** là phương pháp thiết kế phần mềm tập trung vào **business domain**, dùng **Ubiquitous Language** để developer và domain expert nói cùng một "ngôn ngữ".

Các khái niệm cốt lõi:

| Khái niệm | Định nghĩa | Ví dụ trong EcomAI |
|---|---|---|
| **Entity** | Có ID duy nhất, tồn tại xuyên suốt vòng đời | `User`, `Address`, `Order` |
| **Value Object** | Không có ID, so sánh bằng giá trị, bất biến | `FullName` (first_name, last_name) |
| **Aggregate / Aggregate Root** | Nhóm entity liên kết chặt, truy cập qua root | `User` là Aggregate Root, chứa `FullName` (1-1) và `Address` (1-N); `Order` là Aggregate Root chứa `OrderItem` |
| **Bounded Context** | Ranh giới rõ ràng của 1 domain | Mỗi microservice = 1 Bounded Context |
| **Domain Service** | Business logic không thuộc Entity nào | `PriceCalculationService` |
| **Repository** | Truy xuất Aggregate | Django ORM QuerySet |
| **Anti-Corruption Layer (ACL)** | Chuẩn hóa data giữa các context | Serializer/Adapter trong `views.py`, AI Service dùng ACL để chuẩn hóa dữ liệu từ Product |

#### Áp dụng cụ thể — User Service

```python
class User(AbstractUser):          # << Aggregate Root >>
    role = models.CharField(...)   # admin|staff|customer

class FullName(models.Model):      # Value Object (1-1 với User)
    user = models.OneToOneField(User, related_name='full_name')
    last_name, first_name = ...

class Address(models.Model):       # Entity (1-N với User)
    user = models.ForeignKey(User, related_name='addresses')
    address_line, is_default = ...
```

→ Aggregate Root (`User`) chỉ chứa identity/role/credentials; các thuộc tính mô tả (tên đầy đủ, địa chỉ) tách thành VO/Entity riêng.

#### Context Map (7 Bounded Context)

```
User Context  <--Shared Kernel (user_id)--> Order Context
     |                                            |
Customer-Supplier                       Customer-Supplier
     v                                            v
Product Context                          Payment Context
     |                                            |
     +-------------------+----------------------+
                          v
                    AI Context
              (RNN/LSTM/BiLSTM, KB_Graph,
               Graph-RAG, Recommendation)
```

- **Shared Kernel**: `user_id` được chia sẻ giữa các service (không share DB, chỉ share khái niệm)
- **Customer-Supplier**: Order phụ thuộc Product; AI phụ thuộc Product
- **Anti-Corruption Layer**: AI Service chuẩn hóa dữ liệu Product trước khi đưa vào KB_Graph/RAG

### 2.2 RAG (Retrieval-Augmented Generation) là gì?

**RAG** kết hợp:
1. **Retrieval**: tìm kiếm thông tin/sản phẩm liên quan từ knowledge base
2. **Generation**: sinh câu trả lời tự nhiên dựa trên thông tin tìm được

Ưu điểm so với LLM thuần: **cập nhật sản phẩm mới mà không cần retrain**.

#### Áp dụng trong EcomAI — `ai-service/rag/pipeline.py` (RAGLite)

Pipeline cho chatbot tư vấn (`POST /chatbot`):

```
User query "tôi cần laptop gaming dưới 20 triệu"
   │
   ▼ [1] KEYWORD MATCHING — xác định keyword "laptop"
   ▼ [2] RETRIEVAL — tra PRODUCT_KEYWORDS dict, lấy top-N sản phẩm + relevance_score
   ▼ [3] AUGMENT — build context: "Sản phẩm liên quan: 1. Laptop ASUS ROG G15..."
   ▼ [4] GENERATE — template/LLM sinh câu trả lời tiếng Việt
   ▼
Response: {answer, recommended_products, image_url, sources}
```

- Bản đầy đủ (`ProductVectorStore` trong `pipeline.py`) dùng **ChromaDB + SentenceTransformer** (`paraphrase-multilingual-MiniLM-L12-v2`) để embedding + similarity search thật, có thể gọi OpenAI GPT-3.5 (`_call_llm`) khi có `OPENAI_API_KEY`, có fallback `_mock_response` khi không có key.
- Bản demo (`main.py` — `RAGLite`) dùng **keyword matching** thuần (dict `PRODUCT_KEYWORDS`/`RESPONSES`), không cần API key, đủ để chạy demo nhanh.

### 2.3 Knowledge Base / KB_Graph là gì?

**Knowledge Base (KB)** ở đây là một **đồ thị tri thức (Knowledge Graph)** lưu quan hệ giữa User và Product, được dùng làm "bộ nhớ ngữ cảnh" cho cả recommendation và chatbot — thay vì chỉ tra cứu văn bản, hệ thống truy vấn **quan hệ có cấu trúc** (User → Product, Product → Product).

KB_Graph gồm các loại node và quan hệ:

| Loại | Tên | Ý nghĩa |
|---|---|---|
| Node | `User`, `Product` | Thực thể |
| Relationship | `VIEWED`, `CLICKED`, `ADDED_TO_CART` | Hành vi thực tế (từ `user_behavior_log.csv`) |
| Relationship | `CO_OCCURS` | 2 sản phẩm cùng được 1 user tương tác |
| Relationship | `PREDICTED_NEXT_ACTION` | Hành động dự đoán tiếp theo, sinh bởi `model_best` (BiLSTM) |

Pipeline xây dựng/cập nhật KB_Graph:

```
Frontend (view/click/add_to_cart)
   → POST /events/ → Product Service
       → lưu DB (user_behavior_events) + ghi user_behavior_log.csv
   → AI Service đọc file (volume mount read-only)
       → build_kb_graph.py: mỗi 120s (background) hoặc POST /graph/refresh
       → ghi node/relationship vào Neo4j
```

### 2.4 Neo4j là gì? Áp dụng ra sao?

**Neo4j** là một **graph database** — lưu dữ liệu dạng node + relationship (thay vì bảng), tối ưu cho truy vấn quan hệ nhiều cấp (ví dụ "sản phẩm nào hay được mua cùng sản phẩm X", "user này có khả năng làm gì tiếp theo").

Trong EcomAI:
- Image: `neo4j:5-community`, port `7474` (Browser UI) / `7687` (Bolt protocol)
- Auth: `neo4j/password123`, kết nối qua `neo4j` Python driver (`NEO4J_URI=bolt://neo4j:7687`)
- Là hạ tầng dùng chung cho **AI Context**, không phải database-per-service của một microservice nghiệp vụ
- `ai-service/rag/graph_rag.py` truy vấn KB_Graph để:
  - Lấy lịch sử tương tác (`VIEWED`/`CLICKED`/`ADDED_TO_CART`) của user
  - Lấy `PREDICTED_NEXT_ACTION` (sinh bởi BiLSTM) + độ tin cậy (confidence)
  - Lấy sản phẩm liên quan qua `CO_OCCURS`
  - Fallback sang sản phẩm phổ biến toàn hệ thống nếu user chưa có lịch sử (cold-start)

**Graph-RAG** = kết hợp RAG keyword (mục 2.2) + ngữ cảnh cá nhân hóa từ KB_Graph (mục 2.3/2.4): nếu `model_best` dự đoán user sắp `add_to_cart` với confidence > 50%, chatbot tự động chèn thêm gợi ý cá nhân hóa vào câu trả lời.

`/recommend` **ưu tiên KB_Graph** (`model: "KB_Graph (BiLSTM)"`); nếu KB_Graph chưa có dữ liệu cho user (user mới/chưa refresh) → fallback **LSTM demo (numpy)** dùng `behavior_sequence` truyền vào.

---

## 3. Các Model AI dùng trong dự án — Vì sao chọn? Kết quả?

### 3.1 Bài toán

Cho **7 hành vi gần nhất** của một user (mỗi hành vi = `product_id` + `action`), dự đoán **loại hành động ở bước thứ 8**, thuộc 1 trong 3 lớp: `view` / `click` / `add_to_cart`.

Lý do bài toán này: user có pattern hành vi tuần tự (xem nhiều sản phẩm cùng danh mục → có xu hướng `add_to_cart`); dự đoán này dùng để sinh quan hệ `PREDICTED_NEXT_ACTION` trong KB_Graph.

### 3.2 Ba kiến trúc được huấn luyện và so sánh

Thay vì chọn sẵn 1 model, đồ án **huấn luyện và so sánh thực nghiệm 3 mạng hồi quy** trên cùng dữ liệu, hyperparameter, seed — rồi chọn `model_best` theo **F1 macro**.

```
product_seq (B,7)        action_seq (B,7)
      │                         │
      ▼                         ▼
 Embedding(18,16)          Embedding(3,16)     padding_idx=0
      │                         │
      └───────────┬─────────────┘
                   ▼  concat → (B,7,32)
        ┌─────────────────────────┐
        │  RNN | LSTM | BiLSTM     │  hidden_dim=32, num_layers=1
        └─────────────────────────┘
                   ▼  hidden state bước cuối (B,32) hoặc (B,64) nếu BiLSTM
              Dropout(0.2)
                   ▼
            Linear(out_dim, 3)
                   ▼
       logits: P(view), P(click), P(add_to_cart)
```

| Model | Vì sao chọn để thử | Đặc điểm |
|---|---|---|
| **RNN** | Baseline đơn giản, ít tham số | Ít overfit khi data nhỏ, nhưng nắm ngữ cảnh kém |
| **LSTM** | Có cổng (gate) ghi nhớ dài hạn | Nhiều tham số hơn RNN, dễ overfit khi data ít |
| **BiLSTM** | Xử lý chuỗi 2 chiều (xuôi + ngược) | Nắm ngữ cảnh đầy đủ nhất, nhiều tham số nhất |

Huấn luyện (`ai-service/training/train_compare.py`): `EPOCHS=30`, `BATCH_SIZE=32`, `LR=0.001`, optimizer Adam, loss `CrossEntropyLoss`, dữ liệu `data_user500.csv` (500 user × 8 hành vi), chia Train/Val/Test = 70/15/15.

### 3.3 Kết quả thực nghiệm

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |
|---|---|---|---|---|
| RNN | 0.5867 | 0.5171 | 0.5448 | 0.5147 |
| LSTM | 0.5733 | 0.4545 | 0.5143 | 0.4701 |
| **BiLSTM** | **0.5867** | **0.5303** | **0.5477** | **0.5267** |

**Nhận xét:**
- **RNN**: đơn giản, ít overfit (gap train/val = 0.1838) — phương án dự phòng ổn định.
- **LSTM**: dễ overfit khi data ít (gap = 0.2648), F1 macro thấp nhất (0.4701).
- **BiLSTM**: dù overfit rõ hơn (gap = 0.3095), vẫn đạt **F1 macro cao nhất trên test (0.5267)** nhờ nắm được pattern "xem nhiều sản phẩm cùng danh mục → sắp add_to_cart".

→ **`model_best` = BiLSTM** (F1 macro = 0.5267, Accuracy = 0.5867), lưu tại `training/model_best.pt` + metadata `training/model_best.json`. Model này sinh quan hệ `PREDICTED_NEXT_ACTION` trong KB_Graph (Neo4j), phục vụ trực tiếp `/recommend` và `/chatbot`. KB_Graph được refresh định kỳ (120s) từ `user_behavior_log.csv` → dự đoán luôn theo hành vi mới nhất.

### 3.4 Các "model" khác trong AI Service

| Tên | Loại | Vai trò |
|---|---|---|
| `SequenceClassifier` (RNN/LSTM/BiLSTM) | PyTorch (CPU) | Dự đoán hành động tiếp theo → sinh `PREDICTED_NEXT_ACTION` cho KB_Graph |
| `LSTMLite` (numpy demo) | Mô phỏng | Fallback `/recommend` khi KB_Graph chưa có dữ liệu — tính cosine similarity giữa embedding ngẫu nhiên |
| `RAGLite` (keyword matching) | Rule-based | Chatbot demo, không cần API key |
| `ProductVectorStore` (ChromaDB + SentenceTransformer) | Embedding model | Bản RAG đầy đủ — similarity search ngữ nghĩa (production) |
| LLM (GPT-3.5, qua OpenAI API) | LLM | Sinh câu trả lời tự nhiên nếu có `OPENAI_API_KEY`, có mock fallback |

---

## 4. Giao tiếp giữa các Service (Inter-service API calls)

### 4.1 Nguyên tắc

- Mọi request từ client đi qua **API Gateway (Nginx, port 80)**: routing theo path prefix, rate limiting (`60 req/phút` API thường, `20 req/phút` cho `/auth/`), CORS, JWT validation.
- Giữa các service **không gọi qua Gateway** — gọi trực tiếp bằng **Docker internal DNS** (`http://<service-name>:<port>`), dùng thư viện `requests` (Django) hoặc `httpx` (FastAPI).
- Có `try/except` quanh các lời gọi liên service → **Fault Isolation** (1 service down không kéo sập service gọi nó).

### 4.2 Gateway routing (nginx.conf)

| Path prefix | Forward đến |
|---|---|
| `/auth/` | `user-service:8000` (rate limit riêng) |
| `/users/` | `user-service:8000` |
| `/products/`, `/categories/`, `/events/` | `product-service:8001` |
| `/cart/` | `cart-service:8002` |
| `/orders/` | `order-service:8003` |
| `/payment/` | `payment-service:8004` |
| `/shipping/` | `shipping-service:8005` |
| `/recommend`, `/chatbot`, `/health` | `ai-service:8006` |
| `/` (catch-all) | `frontend:3000` |

### 4.3 Bảng các lời gọi service-to-service (đồng bộ, REST)

| Service gọi | Gọi đến | Endpoint | Mục đích |
|---|---|---|---|
| cart-service | product-service | `GET /products/{id}/` | Lấy giá/tên/tồn kho để thêm vào giỏ |
| order-service | cart-service | `GET /cart/?user_id=...` | Lấy giỏ hàng để tạo Order + OrderItem |
| order-service | cart-service | `DELETE /cart/clear/{user_id}/` | Xóa giỏ sau khi tạo order |
| payment-service | order-service | `PATCH /orders/{id}/status/` (status=paid) | Cập nhật đơn hàng đã thanh toán |
| payment-service | shipping-service | `POST /shipping/create/` | Tạo shipment sau khi thanh toán thành công |
| shipping-service | order-service | `PATCH /orders/{id}/status/` (status=shipping → delivered) | Đồng bộ trạng thái đơn hàng theo vận chuyển |
| ai-service | product-service | `GET /products/{id}/` | "Enrich" kết quả gợi ý (LSTM demo) với thông tin sản phẩm thật |
| ai-service | Neo4j (Bolt 7687) | Cypher queries | Đọc/viết KB_Graph (`graph_rag.py`, `build_kb_graph.py`) |
| Tất cả service | user-service | `GET /auth/verify/` (hoặc decode JWT cùng secret) | Xác thực JWT nội bộ |

Cấu hình URL các service phụ thuộc được truyền qua **biến môi trường** trong `docker-compose.yml`, ví dụ:

```yaml
cart-service:
  environment:
    PRODUCT_SERVICE_URL: http://product-service:8001

order-service:
  environment:
    CART_SERVICE_URL: http://cart-service:8002
    PAYMENT_SERVICE_URL: http://payment-service:8004

payment-service:
  environment:
    ORDER_SERVICE_URL: http://order-service:8003
    SHIPPING_SERVICE_URL: http://shipping-service:8005

shipping-service:
  environment:
    ORDER_SERVICE_URL: http://order-service:8003

ai-service:
  environment:
    PRODUCT_SERVICE_URL: http://product-service:8001
    NEO4J_URI: bolt://neo4j:7687
```

### 4.4 Luồng mua hàng end-to-end (tổng hợp các lời gọi trên)

```
Customer → Gateway → user-service        : login, nhận JWT
Customer → Gateway → product-service     : xem/tìm sản phẩm
Customer → Gateway → cart-service        → product-service : thêm vào giỏ (verify giá/tồn)
Customer → Gateway → order-service       → cart-service    : tạo order từ giỏ, rồi clear giỏ
Customer → Gateway → payment-service     → order-service   : cập nhật status=paid
                                          → shipping-service: tạo shipment (tracking_code)
shipping-service                          → order-service   : cập nhật status=shipping/delivered (webhook)
Customer → Gateway → ai-service           → product-service + Neo4j : /recommend, /chatbot
```

### 4.5 JWT — xác thực giữa các service

```
1. POST /auth/login/ → user-service xác thực → trả access_token (1h) + refresh_token (7 ngày)
2. Client lưu token (localStorage)
3. Mọi request kèm header Authorization: Bearer <access_token>
4. user-service expose GET /auth/verify/ — service khác gọi để xác thực
   (hoặc decode JWT cục bộ bằng secret key chung — stateless)
5. Token hết hạn → POST /auth/token/refresh/ { refresh_token } → access_token mới
```
