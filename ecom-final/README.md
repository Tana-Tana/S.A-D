# EcomAI — E-Commerce Microservices + AI Service

Hệ thống thương mại điện tử theo kiến trúc Microservices (Django/FastAPI) kèm AI Service
(RNN/LSTM/BiLSTM + Knowledge Graph Neo4j + Graph-RAG Chatbot), triển khai bằng Docker Compose.

## 1. Yêu cầu môi trường

- Docker Desktop (Windows/Mac/Linux), đã bật Docker Compose v2
- Cổng trống: `80`, `3000`, `8000-8006`, `7474`, `7687`

## 2. Khởi động toàn bộ hệ thống

```bash
cd ecom-final/infrastructure
docker compose up -d --build
```

Lệnh trên sẽ build và chạy toàn bộ:

| Service | Port | Mô tả |
|---|---|---|
| `api-gateway` (Nginx) | 80 | Cổng vào duy nhất, route tới các service |
| `frontend` | 3000 | Giao diện web (HTML/CSS/JS) |
| `user-service` | 8000 | Xác thực, tài khoản (MySQL) |
| `product-service` | 8001 | Sản phẩm, danh mục, log hành vi (PostgreSQL) |
| `cart-service` | 8002 | Giỏ hàng (PostgreSQL) |
| `order-service` | 8003 | Đơn hàng (PostgreSQL) |
| `payment-service` | 8004 | Thanh toán (PostgreSQL) |
| `shipping-service` | 8005 | Vận chuyển (PostgreSQL) |
| `ai-service` | 8006 | Recommend/Chatbot (PyTorch + Neo4j) |
| `neo4j` | 7474 (UI), 7687 (bolt) | Knowledge Graph |
| `redis` | — | Cache nội bộ |

> Các service Django tự động `migrate` + seed dữ liệu mẫu khi container khởi động lần đầu
> (`seed_users`, `seed_data`...).

## 3. Truy cập hệ thống

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:80
- **Neo4j Browser**: http://localhost:7474 (user: `neo4j`, password: `password123`)
- **AI Service docs (Swagger)**: http://localhost:8006/docs

### Tài khoản demo (seed sẵn)

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@123` | admin |
| `staff01` | `Staff@123` | staff |
| `customer` | `Customer@123` | customer |

## 4. Kiểm tra trạng thái

```bash
docker compose ps
docker compose logs -f ai-service   # xem log 1 service cụ thể
```

## 5. Ghi chú AI Service

- `model_best` hiện tại là **BiLSTM** (so sánh với RNN/LSTM, xem `ai-service/training/REPORT.md`).
- Hành vi người dùng (view/click/add_to_cart) trên frontend được ghi vào
  `product-service/data/user_behavior_log.csv` (mount sang `ai-service`, chỉ đọc).
- KB_Graph (Neo4j) tự động làm mới mỗi 120 giây từ dữ liệu hành vi mới nhất, hoặc gọi thủ công:
  ```bash
  curl -X POST http://localhost:8006/graph/refresh
  ```

## 6. Dừng hệ thống

```bash
cd ecom-final/infrastructure
docker compose down          # dừng và xóa container, giữ lại volume (DB data)
# docker compose down -v     # (tuỳ chọn) xóa luôn volume - mất toàn bộ dữ liệu DB
```
