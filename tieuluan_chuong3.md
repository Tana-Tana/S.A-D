# CHƯƠNG 3: AI SERVICE CHO TƯ VẤN SẢN PHẨM

---

## 3.1 Mô tả Yêu cầu và Pipeline Tổng thể

### 3.1.1 Yêu cầu AI Service

AI Service được xây dựng nhằm cá nhân hóa trải nghiệm mua sắm thông qua hai chức năng chính:

| Chức năng | Mô tả | Input | Output |
|-----------|-------|-------|--------|
| **Recommendation** | Gợi ý sản phẩm theo hành vi | Chuỗi product_id đã xem/click | Top-K sản phẩm |
| **Chatbot tư vấn** | Trả lời câu hỏi về sản phẩm bằng tiếng Việt | Câu hỏi tự nhiên | Câu trả lời + product cards |

### 3.1.2 Pipeline Tổng thể

```
  Frontend (view/click/add_to_cart that)
       |  POST /events/
       v
  Product Service --> luu DB (user_behavior_events)
       |              + ghi /app/data/user_behavior_log.csv (file thuc, doc duoc)
       |
       v  (volume mount, read-only)
  +-----------------------------------------------------------------+
  |                  AI SERVICE (FastAPI Port 8006)                  |
  |                                                                   |
  |   user_behavior_log.csv                                          |
  |          |                                                       |
  |          v   (background refresh moi 120s, hoac POST /graph/refresh)
  |   +-------------------+        +---------------------------+     |
  |   |  model_best       |  ---->  |   Knowledge Graph (Neo4j) |     |
  |   |  (BiLSTM, PyTorch)|         |   User/Product/CO_OCCURS/ |     |
  |   +-------------------+         |   PREDICTED_NEXT_ACTION   |     |
  |                                  +-------------+-------------+     |
  |                                                |                   |
  |   User Query (text) -->  RAG (keyword)        |                   |
  |          |                    |               |                   |
  |          v                    v               v                   |
  |   +----------------------------------------------------+         |
  |   |        Graph-RAG: gop ngu canh KB_Graph + RAG       |         |
  |   +------------------------+-----------------------------+         |
  +-------------------------------|----------------------------------+
                                   v
                        +----------------------+
                        |    Product Service   |
                        |   (lay thong tin)    |
                        +----------------------+
                                   |
                                   v
                        /recommend , /chatbot --> Top-K + cau tra loi
```

---

## 3.2 Deep Learning — So sánh RNN / LSTM / BiLSTM

### 3.2.1 Bài toán & lý do so sánh 3 kiến trúc

Thay vì chọn sẵn một kiến trúc, đồ án **huấn luyện và so sánh thực nghiệm 3 mạng hồi quy** — RNN, LSTM, BiLSTM — trên cùng một bài toán, sau đó chọn ra `model_best` dựa trên kết quả đo được (mục 3.4):

- **Bài toán**: cho **7 hành vi gần nhất** của một user (mỗi hành vi gồm `product_id` + `action`), dự đoán **loại hành động (action)** ở bước tiếp theo, thuộc 1 trong 3 lớp: `view` / `click` / `add_to_cart`.
- **Lý do so sánh thay vì chọn 1 model cố định**:
  - User có **pattern hành vi tuần tự**: xem nhiều sản phẩm cùng danh mục → có xu hướng thêm vào giỏ hàng.
  - RNN đơn giản, ít tham số, ít overfit khi dữ liệu nhỏ; LSTM có cơ chế cổng (gate) ghi nhớ dài hạn; BiLSTM xử lý chuỗi theo cả hai chiều, nắm ngữ cảnh đầy đủ hơn nhưng nhiều tham số hơn.
  - Việc so sánh thực nghiệm giúp lựa chọn `model_best` có cơ sở định lượng (Accuracy, Precision/Recall/F1 macro) thay vì chọn theo lý thuyết.

### 3.2.2 Kiến trúc chung (`models/sequence_models.py`)

```
product_seq (B,7)        action_seq (B,7)
      |                         |
      v                         v
 Embedding(18,16)          Embedding(3,16)     padding_idx=0
      |                         |
      +-----------+-------------+
                  v
            concat -> (B,7,32)
                  v
      +---------------------------+
      |  RNN | LSTM | BiLSTM       |  hidden_dim=32, num_layers=1
      |  (nn.RNN / nn.LSTM,        |  BiLSTM = nn.LSTM(bidirectional=True)
      |   bidirectional=True/False)|
      +---------------------------+
                  v
        hidden state buoc cuoi      (B,32) hoac (B,64) neu BiLSTM
                  v
            Dropout(0.2)
                  v
          Linear(out_dim, 3)
                  v
        logits: P(view), P(click), P(add_to_cart)
```

### 3.2.3 Code mô hình (`ai-service/models/sequence_models.py`)

```python
class SequenceClassifier(nn.Module):
    """Lop co so dung chung cho RNN / LSTM / BiLSTM."""

    def __init__(self, rnn_type='lstm', bidirectional=False,
                 num_products=18, num_actions=3,
                 embed_dim=16, hidden_dim=32, num_classes=3, num_layers=1):
        super().__init__()
        self.product_embed = nn.Embedding(num_products, embed_dim, padding_idx=0)
        self.action_embed  = nn.Embedding(num_actions, embed_dim)

        input_dim = embed_dim * 2
        if rnn_type == 'rnn':
            self.rnn = nn.RNN(input_dim, hidden_dim, num_layers=num_layers,
                              batch_first=True, nonlinearity='tanh',
                              bidirectional=bidirectional)
        elif rnn_type == 'lstm':
            self.rnn = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers,
                               batch_first=True, bidirectional=bidirectional)

        out_dim = hidden_dim * (2 if bidirectional else 1)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(out_dim, num_classes)

    def forward(self, product_seq, action_seq):
        p = self.product_embed(product_seq)
        a = self.action_embed(action_seq)
        x = torch.cat([p, a], dim=-1)        # (B, 7, 32)

        out, _ = self.rnn(x)                 # (B, 7, hidden*directions)
        last = self.dropout(out[:, -1, :])   # hidden state buoc cuoi
        return self.fc(last)                 # (B, 3) logits


def build_model(name: str) -> SequenceClassifier:
    if name == 'rnn':    return SequenceClassifier(rnn_type='rnn',  bidirectional=False)
    if name == 'lstm':   return SequenceClassifier(rnn_type='lstm', bidirectional=False)
    if name == 'bilstm': return SequenceClassifier(rnn_type='lstm', bidirectional=True)
```

### 3.2.4 Huấn luyện & lựa chọn `model_best` (`ai-service/training/train_compare.py`)

Quy trình huấn luyện (`EPOCHS=30`, `BATCH_SIZE=32`, `LR=0.001`, optimizer Adam, loss `CrossEntropyLoss`):

1. Đọc `data/data_user500.csv`, với mỗi user lấy **7 hành vi đầu** làm input, **hành vi thứ 8** làm nhãn (`action_idx`).
2. Chia dữ liệu Train/Val/Test theo tỉ lệ **70/15/15**.
3. Huấn luyện cả 3 kiến trúc (RNN, LSTM, BiLSTM) với cùng seed, cùng hyperparameter.
4. Đánh giá trên tập test (Accuracy, Precision/Recall/F1 macro), vẽ biểu đồ so sánh và confusion matrix.
5. Chọn model có **F1 macro cao nhất** làm `model_best`, lưu trọng số vào `training/model_best.pt` và metadata vào `training/model_best.json`.

```python
best_name = max(MODEL_NAMES, key=lambda n: all_metrics[n]['f1_macro'])
torch.save(models[best_name].state_dict(), MODEL_BEST_PATH)
```

---

## 3.3 Dữ liệu Thử nghiệm

### 3.3.1 Thu thập hành vi thật từ Frontend

Mỗi khi user xem trang chi tiết sản phẩm, click vào sản phẩm, hoặc thêm vào giỏ hàng, frontend gọi `API.logEvent(productId, action)` (`frontend/js/api.js`), gửi `POST /events/` đến **Product Service**:

```python
# product-service/products/models.py
class UserBehaviorEvent(models.Model):
    """Log hanh vi nguoi dung (view/click/add_to_cart) tren san pham,
    dung lam du lieu huan luyen cho AI service (RNN/LSTM/BiLSTM + KB_Graph)."""
    ACTION_CHOICES = (
        ('view', 'Xem'),
        ('click', 'Click'),
        ('add_to_cart', 'Thêm vào giỏ hàng'),
    )
    user_id    = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
```

`BehaviorEventCreateView` (endpoint `POST /events/`) vừa lưu event vào bảng `user_behavior_events`, vừa **append trực tiếp** vào file `data/user_behavior_log.csv` (mount sang AI Service ở chế độ chỉ đọc) — đây chính là "dữ liệu thật" mà `model_best` dùng để suy luận theo thời gian thực (mục 3.1.2).

### 3.3.2 Sinh dữ liệu mô phỏng để huấn luyện (`simulate_behavior`)

Vì dữ liệu thật thu thập trong quá trình demo còn ít, đồ án dùng management command `simulate_behavior` để sinh **500 user x 8 hành vi** (= 4000 dòng) theo 3 persona, ghi vào cùng bảng `user_behavior_events`:

| Persona | Tỉ lệ user | P(view) | P(click) | P(add_to_cart) | Mô tả |
|---|---|---|---|---|---|
| `browser` | 50% | 0.80 | 0.15 | 0.05 | Lướt xem nhiều, ít thao tác |
| `researcher` | 30% | 0.35 | 0.45 | 0.20 | Tìm hiểu kỹ trước khi quyết định |
| `buyer` | 20% | 0.15 | 0.30 | 0.55 | Có xu hướng mua ngay |

- Mỗi user chọn ngẫu nhiên 1 nhóm sản phẩm yêu thích (`electronics` id 1-8, `book` id 9-13, `fashion` id 14-17), 90% hành vi rơi vào nhóm này, 10% khám phá ngẫu nhiên toàn bộ 17 sản phẩm.
- Hiệu ứng **funnel**: càng về cuối chuỗi 8 bước, xác suất `add_to_cart` càng tăng (mô phỏng hành trình "xem nhiều → quyết định mua").
- Sau khi sinh, dùng `export_behavior_csv` để xuất bảng `user_behavior_events` ra `data/data_user500.csv` — đây là dataset dùng để huấn luyện và so sánh RNN/LSTM/BiLSTM ở mục 3.2.4.

### 3.3.3 Định dạng bài toán huấn luyện

Với mỗi user, 8 hành vi `(product_id, action)` được tách thành:
- **Input**: 7 hành vi đầu — `product_seq[0:7]`, `action_seq[0:7]`
- **Label**: `action` của hành vi thứ 8 (1 trong 3 lớp `view`/`click`/`add_to_cart`)

Khi suy luận trực tuyến (real-time), `build_kb_graph.py` lấy **7 hành vi gần nhất** của mỗi user từ `user_behavior_log.csv` làm input cho `model_best`, nên dự đoán luôn phản ánh hành vi mới nhất (mục 3.1.2 và 3.4).

---

## 3.4 Kết quả So sánh

### 3.4.1 Kết quả thực nghiệm (`training/REPORT.md`)

Bài toán: phân loại hành vi (`view` / `click` / `add_to_cart`) ở bước thứ 8 dựa trên 7 hành vi trước đó, dữ liệu `data_user500.csv` (500 user x 8 hành vi, chia Train/Val/Test = 70/15/15).

| Model | Accuracy | Precision (macro) | Recall (macro) | F1 (macro) |
|---|---|---|---|---|
| RNN | 0.5867 | 0.5171 | 0.5448 | 0.5147 |
| LSTM | 0.5733 | 0.4545 | 0.5143 | 0.4701 |
| **BiLSTM** | **0.5867** | **0.5303** | **0.5477** | **0.5267** |

Biểu đồ chi tiết được lưu tại:
- `training/plots/training_curves.png` — Validation loss & accuracy qua các epoch của 3 model.
- `training/plots/confusion_matrices.png` — Confusion matrix trên tập test.
- `training/plots/model_comparison.png` — Biểu đồ cột so sánh 4 metrics.

### 3.4.2 Nhận xét

- **RNN** có kiến trúc đơn giản, ít tham số nhất. Với chuỗi ngắn (7 bước) và tập train nhỏ (~350 mẫu), RNN ít bị overfitting, gap train/val accuracy cuối cùng chỉ 0.1838 — phương án dự phòng ổn định.
- **LSTM** có cơ chế cổng (gate) ghi nhớ dài hạn nhưng nhiều tham số hơn nên dễ overfit khi dữ liệu ít: F1 macro = 0.4701, gap train/val = 0.2648 (cao nhất, kết quả kém nhất trong 3 model).
- **BiLSTM** xử lý chuỗi theo cả hai chiều (xuôi + ngược), nắm bắt ngữ cảnh đầy đủ hơn (ví dụ pattern "xem nhiều sản phẩm cùng danh mục → sắp thêm vào giỏ hàng"). Dù có dấu hiệu overfit rõ hơn trên tập validation (gap = 0.3095), BiLSTM vẫn đạt **F1 macro cao nhất trên tập test (0.5267)**.

=> **Model được chọn làm `model_best`: BiLSTM** (F1 macro = 0.5267, Accuracy = 0.5867). Đây là model dùng để sinh quan hệ `PREDICTED_NEXT_ACTION` trong KB_Graph (Neo4j), phục vụ trực tiếp cho `/recommend` và `/chatbot`. KB_Graph được làm mới định kỳ từ dữ liệu hành vi thực tế (`user_behavior_log.csv`), nên dự đoán của BiLSTM cập nhật theo hành vi gần đây của từng user.

---

## 3.5 RAG Pipeline — Chatbot Tư vấn

### 3.5.1 Giới thiệu RAG

**RAG (Retrieval-Augmented Generation)** kết hợp:
- **Retrieval**: Tìm kiếm sản phẩm liên quan từ knowledge base
- **Generation**: Sinh câu trả lời tự nhiên dựa trên sản phẩm đã tìm

Ưu điểm so với LLM thuần: cập nhật được sản phẩm mới mà không cần retrain.

### 3.5.2 Pipeline RAG chi tiết

```
User: "toi can laptop gaming duoi 20 trieu"
    |
    v
[1. KEYWORD MATCHING]
    Phan tich query -> xac dinh keyword: "laptop"
    -> ket hop voi PRODUCT_KEYWORDS dict
    |
    v
[2. RETRIEVAL]
    Tim san pham thuoc keyword "laptop":
    - Laptop ASUS ROG G15 (2024) — 19.5tr [ID=1, score=0.95]
    - Man hinh LG UltraWide 34" — 9.9tr  [ID=5, score=0.88]
    - Ban phim co Keychron K2 Pro — 2.1tr [ID=7, score=0.81]
    |
    v
[3. AUGMENT]
    Build context: "San pham lien quan: 1. Laptop ASUS ROG G15 ..."
    |
    v
[4. GENERATE]
    Template/LLM sinh cau tra loi:
    "Voi nhu cau laptop gaming duoi 20 trieu, toi goi y ASUS ROG G15..."
    |
    v
Response: {answer: "...", recommended_products: [...], image_url: [...]}
```

### 3.5.3 Graph-RAG: kết hợp KB_Graph với RAG keyword

Ngoài luồng RAG keyword ở trên, `/chatbot` còn gọi `graph_rag.build_context(user_id)` (`ai-service/rag/graph_rag.py`) để lấy **ngữ cảnh hành vi cá nhân** từ KB_Graph:

- Lấy lịch sử tương tác (`VIEWED`/`CLICKED`/`ADDED_TO_CART`) của user trong Neo4j.
- Lấy hành động dự đoán tiếp theo (`PREDICTED_NEXT_ACTION`, sinh bởi `model_best`) cùng độ tin cậy.
- Lấy sản phẩm liên quan (`CO_OCCURS`) với sản phẩm được dự đoán.
- Nếu user chưa có lịch sử, fallback sang sản phẩm phổ biến toàn hệ thống (`ADDED_TO_CART` nhiều nhất).

Nếu `model_best` dự đoán user sắp `add_to_cart` với độ tin cậy > 50%, chatbot tự động chèn thêm gợi ý vào câu trả lời thông qua `graph_rag.describe(user_id)`:

```python
# ai-service/main.py — chatbot endpoint
@app.post("/chatbot")
async def chatbot(req: ChatRequest):
    """Chatbot tu van san pham (RAG keyword) + ngu canh KB_Graph (model_best)."""
    products = rag.search(req.message, n=5)
    answer   = rag.generate(req.message, products)

    ctx = graph_rag.build_context(req.user_id)
    graph_note = graph_rag.describe(req.user_id)

    if ctx["predicted_action"] == "add_to_cart" and (ctx["confidence"] or 0) > 0.5:
        answer += f" Ngoài ra, {graph_note}"

    return {
        "user_id":              req.user_id,
        "question":             req.message,
        "answer":               answer,
        "recommended_products": products,
        "graph_context":        ctx,
        "sources":              [p["name"] for p in products],
        "model":                "RAG (keyword) + KB_Graph (model_best)",
    }
```

Ví dụ `graph_note` sinh ra: *"Theo KB_Graph (model BiLSTM), user 50 có khả năng sẽ 'thêm vào giỏ hàng' tiếp theo với độ tin cậy 74%. Các sản phẩm liên quan: [2, 5, 8]."*

---

## 3.6 Tích hợp vào E-Commerce

### 3.6.1 Thu thập hành vi từ Frontend

Frontend gọi `API.logEvent(productId, action)` (`frontend/js/api.js`) để gửi `POST /events/` mỗi khi:

| Trang | Hành động | Action |
|---|---|---|
| `index.html`, `products.html` | Click vào card sản phẩm | `click` |
| `product-detail.html` | Mở trang chi tiết sản phẩm | `view` |
| `js/api.js` (`Cart.add`) | Thêm sản phẩm vào giỏ hàng | `add_to_cart` |

Các event này được Product Service ghi vào bảng `user_behavior_events` và file `data/user_behavior_log.csv`, làm đầu vào cho vòng lặp refresh KB_Graph nền của AI Service (mục 3.1.2).

### 3.6.2 Recommendation Widget (Trang chủ)

Phần gợi ý AI trên trang chủ hiển thị sản phẩm được cá nhân hóa dựa trên KB_Graph.

API call: `GET /recommend/graph?user_id=1&top_k=5` (hoặc `POST /recommend` với `user_id` — tự động ưu tiên KB_Graph, fallback sang LSTM demo nếu KB_Graph chưa sẵn sàng).

### 3.6.3 Chatbot Widget (Tất cả trang)

Chatbot floating button góc phải màn hình, hiển thị:
- Text trả lời tự nhiên tiếng Việt, có thể kèm gợi ý dựa trên `model_best` (mục 3.5.3)
- Card sản phẩm với ảnh, giá, nút **Xem** + **Thêm giỏ**
- Lịch sử chat lưu vào localStorage, khôi phục khi mở lại
- Xóa lịch sử bằng nút "Xóa"

### 3.6.4 Ví dụ Response mẫu

```json
POST /recommend
{"user_id": 50, "top_k": 5}

Response 200 OK:
{
  "user_id": 50,
  "model": "KB_Graph (BiLSTM)",
  "predicted_action": "view",
  "confidence": 0.743,
  "note": "",
  "recommendations": [
    {"product_id": 2, "name": "iPhone 15 Pro Max", "product_type": "electronics", "price": "29990000", ...},
    {"product_id": 5, "name": "Man hinh LG UltraWide 34\"", "product_type": "electronics", "price": "9900000", ...}
  ]
}
```

```json
POST /chatbot
{"user_id": 50, "message": "toi can laptop gaming duoi 20 trieu"}

Response 200 OK:
{
  "answer": "Voi nhu cau laptop gaming duoi 20 trieu, toi goi y Laptop ASUS ROG G15 (2024). Ngoai ra, theo KB_Graph (model BiLSTM), user 50 co kha nang se 'them vao gio hang' tiep theo voi do tin cay 74%. Cac san pham lien quan: [2, 5, 8].",
  "recommended_products": [
    {
      "product_id": "1",
      "name": "Laptop ASUS ROG G15 (2024)",
      "product_type": "electronics",
      "price": "19500000",
      "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=480&q=80",
      "relevance_score": 0.95
    }
  ],
  "graph_context": {
    "product_ids": [2, 5, 8],
    "predicted_action": "add_to_cart",
    "confidence": 0.74,
    "model_name": "BiLSTM",
    "note": ""
  },
  "model": "RAG (keyword) + KB_Graph (model_best)"
}
```

---

## 3.7 Triển khai AI Service

### 3.7.1 Tech Stack

| Component | Technology | Lý do chọn |
|-----------|-----------|------------|
| **API Framework** | FastAPI 0.104 | Async, tự động OpenAPI docs |
| **Deep Learning** | PyTorch (CPU) — RNN/LSTM/BiLSTM (`SequenceClassifier`) | So sánh thực nghiệm, chọn `model_best` theo F1 macro |
| **Knowledge Graph** | Neo4j | Lưu User/Product/CO_OCCURS/PREDICTED_NEXT_ACTION, truy vấn ngữ cảnh nhanh |
| **Data processing** | pandas | Đọc/biến đổi `user_behavior_log.csv`, `data_user500.csv` |
| **Chatbot** | RAG keyword (RAGLite) + Graph-RAG (KB_Graph) | Có fallback, không cần API key, cá nhân hóa theo `model_best` |
| **Background job** | asyncio (`run_in_executor`) | Refresh KB_Graph định kỳ từ dữ liệu hành vi thực tế, không block API |
| **Container** | Docker / Docker Compose | Volume mount chia sẻ `user_behavior_log.csv` giữa Product Service và AI Service |

### 3.7.2 Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8006
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
```

### 3.7.3 Kiến trúc volume mount cho dữ liệu thời gian thực

```yaml
# infrastructure/docker-compose.yml
product-service:
  volumes:
    - ../product-service/data:/app/data        # ghi user_behavior_log.csv

ai-service:
  volumes:
    - ../product-service/data:/app/live_data:ro  # doc lai (read-only)
```

Nhờ đó AI Service luôn đọc được phiên bản mới nhất của `user_behavior_log.csv` mà không cần build lại image, còn vòng lặp nền (`KB_GRAPH_REFRESH_SECONDS`, mặc định 120s) hoặc endpoint `POST /graph/refresh` sẽ build lại KB_Graph từ dữ liệu này.

---

## 3.8 Kết luận Chương 3

AI Service đã được xây dựng thành công với:
- **So sánh 3 kiến trúc RNN/LSTM/BiLSTM** trên cùng bài toán phân loại hành vi tiếp theo; chọn **BiLSTM làm `model_best`** (F1 macro = 0.5267, Accuracy = 0.5867).
- **KB_Graph (Neo4j)**: biểu diễn User/Product cùng các quan hệ `VIEWED`/`CLICKED`/`ADDED_TO_CART`/`CO_OCCURS`/`PREDICTED_NEXT_ACTION`, sinh từ `model_best`.
- **Pipeline dữ liệu thời gian thực**: hành vi view/click/add_to_cart từ frontend được ghi vào `user_behavior_log.csv` và tự động làm mới KB_Graph (background refresh / `POST /graph/refresh`), giúp `/recommend` và `/chatbot` phản ánh hành vi gần nhất của user mà không cần huấn luyện lại thủ công.
- **Graph-RAG Chatbot**: kết hợp RAG keyword (gợi ý sản phẩm theo truy vấn) với ngữ cảnh cá nhân hóa từ KB_Graph (`graph_context`, `graph_note`).
- **Tích hợp E-Commerce**: recommendation widget và chatbot trên mọi trang, lịch sử chat lưu/khôi phục từ localStorage.
