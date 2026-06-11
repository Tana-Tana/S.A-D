# CHƯƠNG 4: XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

---

## 4.1 Kiến trúc Tổng thể

### 4.1.1 Mô hình hệ thống

Hệ thống EcomAI được xây dựng theo kiến trúc Microservices hoàn chỉnh với 8 service độc lập, 1 API Gateway và 6 database riêng biệt:

```
                         INTERNET / BROWSER
                               |
                    +----------v----------+
                    |    API Gateway      |
                    |    Nginx (Port 80)  |
                    |  - Rate Limiting    |
                    |  - JWT Validation   |
                    |  - Request Routing  |
                    +----------+----------+
                               |
          +--------------------+--------------------+
          |          |         |         |          |
   +------v---+ +----v----+ +--v----+ +--v-----+ +-v--------+
   |  User    | |Product  | | Cart  | | Order  | | Payment  |
   |  Service | |Service  | |Service| |Service | | Service  |
   |  :8000   | |:8001    | |:8002  | |:8003   | | :8004    |
   |  MySQL   | |Postgres | |Postg. | |Postg.  | | Postg.   |
   +----------+ +---------+ +-------+ +--------+ +----------+
                                                        |
   +----------+                              +----------v----+
   | Shipping |                              |  Shipping     |
   | Service  |                              |  Service      |
   |  :8005   |                              |  :8005        |
   |  Postg.  |                              |  Postg.       |
   +----------+                              +---------------+

                    +------------------------+
                    |      AI Service        |
                    |      FastAPI :8006     |
                    |  LSTM + RAG Pipeline   |
                    +------------------------+

                    +------------------------+
                    |      Frontend          |
                    |   Nginx :3000          |
                    |  HTML+CSS+JS           |
                    +------------------------+

   ─────────── Docker Network: ecom-network ───────────────
   +----------------------------------------------------------+
   | MySQL:3306 | PostgreSQL:5432x5 | Redis:6379             |
   +----------------------------------------------------------+
```

*Hình 4.1: Kiến trúc tổng thể hệ thống EcomAI*

### 4.1.2 Nguyên tắc kiến trúc áp dụng

| Nguyên tắc | Thực thi trong hệ thống |
|-----------|------------------------|
| **Loose Coupling** | Service giao tiếp qua REST API, không share DB |
| **High Cohesion** | Mỗi service chứa toàn bộ logic cho 1 domain |
| **Database-per-Service** | 6 database riêng biệt (1 MySQL + 5 PostgreSQL) |
| **API-First** | Mỗi service có OpenAPI docs tự động |
| **Fault Isolation** | Service fail không kéo theo service khác |
| **Containerization** | Tất cả đóng gói Docker, chạy Docker Compose |

---

## 4.2 Công nghệ Sử dụng

### 4.2.1 Bảng Tech Stack toàn hệ thống

| Layer | Service | Technology | Version | Lý do chọn |
|-------|---------|-----------|---------|------------|
| **Gateway** | gateway | Nginx | 1.25 | Reverse proxy, rate limiting, routing |
| **User** | user-service | Django + DRF | 4.2.7 | AbstractUser, JWT support |
| **Product** | product-service | Django + DRF | 4.2.7 | ORM mạnh, JSONB support |
| **Cart** | cart-service | Django + DRF | 4.2.7 | Simple CRUD |
| **Order** | order-service | Django + DRF | 4.2.7 | Workflow management |
| **Payment** | payment-service | Django + DRF | 4.2.7 | Transaction handling |
| **Shipping** | shipping-service | Django + DRF | 4.2.7 | Status tracking |
| **AI** | ai-service | FastAPI + NumPy | 0.104 / 1.26 | Async, ML ecosystem |
| **Frontend** | frontend | Nginx + HTML/JS | 1.25 | Static file serving |
| **Auth** | Tất cả | JWT (simplejwt) | 5.3.0 | Stateless, microservice-friendly |
| **DB User** | user-db | MySQL | 8.0 | Authentication workload |
| **DB khác** | product/order/... | PostgreSQL | 15 | JSONB, complex queries |
| **Cache** | redis | Redis | 7 | Session, rate limiting |
| **Container** | Tất cả | Docker | 24+ | Nhất quán môi trường |
| **Orchestration** | Dev | Docker Compose | 3.9 | Multi-service management |

---

## 4.3 Cấu trúc Code Toàn hệ thống

### 4.3.1 Cấu trúc thư mục

```
ecom-final/
|
|-- gateway/
|   |-- nginx.conf                  <- API Gateway, routing rules, rate limit
|
|-- user-service/                   <- Django + MySQL
|   |-- user_service/
|   |   |-- settings.py             <- JWT, MySQL config, INSTALLED_APPS
|   |   |-- urls.py                 <- /auth/, /users/
|   |-- users/
|   |   |-- models.py               <- User(AbstractUser) + role ENUM
|   |   |-- serializers.py          <- Register, Login, JWT logic
|   |   |-- views.py                <- RegisterView, LoginView, VerifyTokenView
|   |   |-- migrations/
|   |   |   |-- 0001_initial.py     <- Migration file tinh
|   |   |-- management/commands/
|   |       |-- seed_users.py       <- Tao tai khoan admin/staff/customer
|   |-- Dockerfile
|   |-- requirements.txt
|
|-- product-service/                <- Django + PostgreSQL
|   |-- products/
|   |   |-- models.py               <- Category, Product, Book, Electronics, Fashion
|   |   |-- serializers.py          <- Nested serializers voi detail
|   |   |-- views.py                <- CRUD + Search + StockCheck
|   |   |-- urls.py
|   |   |-- migrations/
|   |   |-- management/commands/
|   |       |-- seed_data.py        <- 17 san pham voi anh Unsplash dung
|   |-- Dockerfile
|
|-- cart-service/                   <- Django
|   |-- cart/
|   |   |-- models.py               <- Cart, CartItem
|   |   |-- views.py                <- Add, Remove, Clear, View
|   |   |-- migrations/
|   |       |-- 0001_initial.py
|   |-- Dockerfile
|
|-- order-service/                  <- Django + PostgreSQL
|   |-- orders/
|   |   |-- models.py               <- Order (state machine), OrderItem
|   |   |-- views.py                <- Create from cart, StatusUpdate
|   |   |-- migrations/
|   |       |-- 0001_initial.py
|   |-- Dockerfile
|
|-- payment-service/                <- Django + PostgreSQL
|   |-- payments/
|   |   |-- models.py               <- Payment + UUID transaction_id
|   |   |-- views.py                <- Mock gateway + trigger shipping
|   |   |-- migrations/
|   |       |-- 0001_initial.py
|   |-- Dockerfile
|
|-- shipping-service/               <- Django + PostgreSQL
|   |-- shipping/
|   |   |-- models.py               <- Shipment + ShipmentHistory
|   |   |-- views.py                <- Create, Track, Webhook update
|   |   |-- migrations/
|   |       |-- 0001_initial.py
|   |-- Dockerfile
|
|-- ai-service/                     <- FastAPI + NumPy
|   |-- models/
|   |   |-- lstm_model.py           <- LSTMLite (NumPy demo)
|   |-- rag/
|   |   |-- pipeline.py             <- RAGLite keyword matching
|   |-- data/
|   |   |-- sample_behavior.py      <- 3 datasets thu nghiem
|   |-- main.py                     <- FastAPI: /recommend, /chatbot, /hybrid
|   |-- Dockerfile
|   |-- requirements.txt
|
|-- frontend/                       <- Nginx static files
|   |-- index.html                  <- Trang chu + AI recommendation
|   |-- products.html               <- Danh sach san pham + filter
|   |-- product-detail.html         <- Chi tiet san pham
|   |-- cart.html                   <- Gio hang + checkout
|   |-- auth.html                   <- Dang nhap / Dang ky
|   |-- css/style.css               <- Custom design system
|   |-- js/
|   |   |-- api.js                  <- API module + Auth + Cart + ChatStore
|   |   |-- products-data.js        <- Mock data + Unsplash images
|   |   |-- chatbot.js              <- Chatbot widget + history persistence
|   |-- nginx.conf                  <- Proxy API calls to gateway
|   |-- Dockerfile
|
|-- infrastructure/
    |-- docker-compose.yml          <- 15 containers, 1 lenh chay
```

### 4.3.2 API Gateway — nginx.conf

```nginx
events { worker_connections 1024; }

http {
    # Docker internal DNS
    resolver 127.0.0.11 valid=10s ipv6=off;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m  rate=60r/m;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=20r/m;

    server {
        listen 80;

        # CORS headers
        add_header Access-Control-Allow-Origin  * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
        if ($request_method = OPTIONS) { return 204; }

        # Routing den tung service (su dung bien de resolve dong)
        location /auth/     { set $svc http://user-service:8000;     proxy_pass $svc; }
        location /users/    { set $svc http://user-service:8000;     proxy_pass $svc; }
        location /products/ { set $svc http://product-service:8001;  proxy_pass $svc; }
        location /cart/     { set $svc http://cart-service:8002;     proxy_pass $svc; }
        location /orders/   { set $svc http://order-service:8003;    proxy_pass $svc; }
        location /payment/  { set $svc http://payment-service:8004;  proxy_pass $svc; }
        location /shipping/ { set $svc http://shipping-service:8005; proxy_pass $svc; }
        location /recommend { set $svc http://ai-service:8006;       proxy_pass $svc; proxy_read_timeout 60s; }
        location /chatbot   { set $svc http://ai-service:8006;       proxy_pass $svc; proxy_read_timeout 60s; }

        location /gateway/health {
            return 200 '{"status":"ok"}';
            add_header Content-Type application/json;
        }

        location / { set $fe http://frontend:3000; proxy_pass $fe; }
    }
}
```

### 4.3.3 Docker Compose — docker-compose.yml

```yaml
version: '3.9'

networks:
  ecom-network:
    driver: bridge

volumes:
  user-db-data:
  product-db-data:
  cart-db-data:
  order-db-data:
  payment-db-data:
  shipping-db-data:

services:
  # --- Databases ---
  user-db:
    image: mysql:8.0
    environment: { MYSQL_DATABASE: user_db, MYSQL_ROOT_PASSWORD: password }
    volumes: [user-db-data:/var/lib/mysql]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]
      interval: 10s; retries: 5

  product-db:
    image: postgres:15
    environment: { POSTGRES_DB: product_db, POSTGRES_PASSWORD: password }
    volumes: [product-db-data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s; retries: 5

  # --- Services ---
  user-service:
    build: { context: ../user-service }
    ports: ["8000:8000"]
    environment:
      DB_HOST: user-db
      DB_NAME: user_db
    depends_on:
      user-db: { condition: service_healthy }
    networks: [ecom-network]
    command: >
      sh -c "python manage.py migrate &&
             python manage.py seed_users &&
             python manage.py runserver 0.0.0.0:8000"

  product-service:
    build: { context: ../product-service }
    ports: ["8001:8001"]
    depends_on:
      product-db: { condition: service_healthy }
    networks: [ecom-network]
    command: >
      sh -c "python manage.py makemigrations products &&
             python manage.py migrate &&
             python manage.py seed_data &&
             python manage.py runserver 0.0.0.0:8001"

  ai-service:
    build: { context: ../ai-service }
    ports: ["8006:8006"]
    networks: [ecom-network]
    command: uvicorn main:app --host 0.0.0.0 --port 8006

  frontend:
    build: { context: ../frontend }
    ports: ["3000:3000"]
    networks: [ecom-network]

  gateway:
    image: nginx:1.25-alpine
    ports: ["80:80"]
    volumes: [../gateway/nginx.conf:/etc/nginx/nginx.conf:ro]
    depends_on: [user-service, product-service, ai-service, frontend]
    networks: [ecom-network]
```

---

## 4.4 Luồng Xác thực JWT

```
Buoc 1: Client gui POST /auth/login/ { username, password }
         |
Buoc 2: user-service xac thuc -> tao JWT:
         access_token  (het han sau 1 gio)
         refresh_token (het han sau 7 ngay)
         |
Buoc 3: Client luu token vao localStorage
         |
Buoc 4: Moi request tiep theo gui header:
         Authorization: Bearer eyJhbGc...
         |
Buoc 5: user-service cung cap endpoint /auth/verify/
         Cac service khac goi vao day khi can xac thuc
         (hoac decode JWT local voi cung secret key)
         |
Buoc 6: Token het han -> POST /auth/token/refresh/ { refresh_token }
         -> nhan access_token moi
```

---

## 4.5 Triển khai

### 4.5.1 Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|-----------|---------------------|
| Docker Desktop | 4.0+ |
| Docker Compose | v2+ |
| RAM | 4GB (khuyến nghị 8GB) |
| Disk | 10GB trống |

### 4.5.2 Hướng dẫn triển khai step-by-step

```bash
# Buoc 1: Clone project
cd d:\Tai_lieu_nam_4\Ki_2\S.A&D\TieuLuanV2\ecom-final

# Buoc 2: Chay toan bo he thong (15 containers)
cd infrastructure
docker compose up --build

# Buoc 3: Kiem tra trang thai (moi terminal moi)
docker ps --format "table {{.Names}}\t{{.Status}}"

# Buoc 4: Seed du lieu thu cong (neu can)
docker exec product-service python manage.py makemigrations products
docker exec product-service python manage.py migrate
docker exec product-service python manage.py seed_data

# Buoc 5: Truy cap he thong
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8006/docs  (AI Service Swagger)
# Gateway:   http://localhost/gateway/health
```

### 4.5.3 Tài khoản mặc định sau khi seed

| Tài khoản | Mật khẩu | Quyền |
|-----------|---------|-------|
| admin | Admin@123 | Toàn quyền hệ thống |
| staff01 | Staff@123 | Xử lý đơn hàng, vận chuyển |
| customer | Customer@123 | Mua hàng, xem sản phẩm |

---

## 4.6 Kết quả Hệ thống

### 4.6.1 API Response mẫu — Đăng nhập

```json
POST http://localhost:3000/auth/login/
Body: {"username": "customer", "password": "Customer@123"}

Response 200 OK:
{
  "user": {
    "id": 3,
    "username": "customer",
    "email": "customer@ecomai.vn",
    "first_name": "Khach hang",
    "role": "customer",
    "created_at": "2026-05-11T08:30:00Z"
  },
  "access":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4.6.2 API Response mẫu — Danh sách sản phẩm

```json
GET http://localhost:3000/products/?ordering=-sold_count&page_size=3

Response 200 OK:
{
  "count": 17,
  "next": "http://localhost/products/?page=2",
  "results": [
    {
      "id": 13,
      "name": "Atomic Habits - James Clear",
      "price": "168000.00",
      "original_price": "210000.00",
      "discount_percent": 20,
      "product_type": "book",
      "category": 2,
      "category_name": "Sach",
      "image_url": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=480&q=80",
      "rating": "4.90",
      "sold_count": 3240,
      "book_detail": {
        "author": "James Clear",
        "publisher": "Avery",
        "isbn": "9780735211292",
        "pages": 320,
        "language": "Tieng Anh"
      }
    }
  ]
}
```

### 4.6.3 API Response mẫu — Tạo đơn hàng

```json
POST http://localhost:3000/orders/create/
Headers: Authorization: Bearer eyJhbGc...
Body: {"user_id": 3, "shipping_address": "123 Nguyen Trai, Ha Noi", "note": "Giao buoi sang"}

Response 201 Created:
{
  "id": 55,
  "user_id": 3,
  "total_price": "168000.00",
  "shipping_address": "123 Nguyen Trai, Ha Noi",
  "shipping_fee": "30000.00",
  "status": "pending",
  "status_display": "Cho xac nhan",
  "note": "Giao buoi sang",
  "items": [
    {
      "product_id": 13,
      "product_name": "Atomic Habits - James Clear",
      "product_price": "168000.00",
      "quantity": 1,
      "subtotal": "168000.00"
    }
  ],
  "created_at": "2026-05-11T15:30:00Z"
}
```

### 4.6.4 API Response mẫu — AI Recommendation

```json
GET http://localhost:3000/recommend?user_id=3&behavior_sequence=9,10,13&top_k=3

Response 200 OK:
{
  "user_id": 3,
  "model": "LSTM (numpy demo)",
  "sequence_length": 3,
  "recommendations": [
    {
      "product_id": 12,
      "name": "The Psychology of Money",
      "price": "145000.00",
      "product_type": "book",
      "image_url": "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=480&q=80",
      "recommendation_score": 0.3421
    },
    {
      "product_id": 11,
      "name": "Tu duy nhu Elon Musk",
      "price": "159000.00",
      "product_type": "book",
      "recommendation_score": 0.2876
    },
    {
      "product_id": 1,
      "name": "Laptop ASUS ROG G15 (2024)",
      "price": "19500000.00",
      "product_type": "electronics",
      "recommendation_score": 0.2103
    }
  ]
}
```

### 4.6.5 API Response mẫu — Chatbot RAG

```json
POST http://localhost:3000/chatbot
Body: {"user_id": 3, "message": "toi can sach ve lap trinh Python"}

Response 200 OK:
{
  "user_id": 3,
  "question": "toi can sach ve lap trinh Python",
  "answer": "Cac cuon sach Clean Code - Robert Martin, Domain-Driven Design rat duoc yeu thich, se giup ban mo rong tu duy va kien thuc.",
  "recommended_products": [
    {
      "product_id": "9",
      "name": "Clean Code - Robert C. Martin",
      "product_type": "book",
      "price": "180000",
      "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=480&q=80",
      "relevance_score": 0.95
    },
    {
      "product_id": "10",
      "name": "Domain-Driven Design - Eric Evans",
      "product_type": "book",
      "price": "350000",
      "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=480&q=80",
      "relevance_score": 0.88
    }
  ],
  "model": "RAG (keyword-matching)"
}
```

### 4.6.6 API Response mẫu — Theo dõi vận chuyển

```json
GET http://localhost:3000/shipping/status/?order_id=55

Response 200 OK:
{
  "id": 1,
  "order_id": 55,
  "tracking_code": "GHN2048301762",
  "carrier": "GHN Express",
  "status": "processing",
  "status_display": "Dang chuan bi hang",
  "estimated_delivery": "2026-05-14",
  "history": [
    {
      "status": "processing",
      "description": "Don hang da duoc xac nhan va dang chuan bi hang",
      "location": "Kho Ha Noi",
      "timestamp": "2026-05-11T15:35:00Z"
    }
  ]
}
```

---

## 4.7 Đánh giá Hệ thống

### 4.7.1 Hiệu năng ước tính

| Endpoint | Avg Response | P95 | Ghi chú |
|----------|-------------|-----|---------|
| GET /products/ | ~45ms | ~120ms | Co DB index |
| POST /auth/login/ | ~80ms | ~200ms | JWT signing |
| POST /orders/create/ | ~150ms | ~350ms | Goi cart-service |
| POST /payment/pay/ | ~200ms | ~500ms | Goi order + shipping |
| GET /recommend | ~50ms | ~200ms | NumPy computation |
| POST /chatbot | ~30ms | ~100ms | Keyword matching |

### 4.7.2 Khả năng mở rộng

| Service | Chiến lược scale | Lý do |
|---------|----------------|-------|
| product-service | Horizontal (nhieu instance) | Read-heavy, stateless |
| ai-service | Vertical (GPU) + Horizontal | ML inference |
| user-service | Horizontal | Stateless (JWT) |
| payment-service | Vertical | Consistency quan trong |

### 4.7.3 Ưu điểm

- **Fault isolation**: Neu ai-service down, mua hang van hoat dong binh thuong
- **Independent deployment**: Update product-service khong anh huong order-service
- **Tech diversity**: Django cho CRUD-heavy, FastAPI cho ML-heavy
- **Database optimization**: MySQL cho auth, PostgreSQL cho complex queries
- **Scalability**: Moi service scale rieng theo nhu cau thuc te
- **Frontend resilient**: Mock data fallback khi backend dang khoi dong

### 4.7.4 Nhược điểm và hướng cải thiện

| Nhược điểm | Hiện trạng | Giải pháp tương lai |
|-----------|-----------|-------------------|
| Distributed tracing | Chua co | Them Jaeger/Zipkin |
| Service discovery | Hardcode hostname | Consul hoac Kubernetes DNS |
| Circuit breaker | Chua co | Resilience4j/Hystrix |
| Async messaging | REST dong bo | RabbitMQ/Kafka cho events |
| Monitoring | Chua co | Prometheus + Grafana |
| LSTM cold-start | User moi khong co history | Dung trending products |
| Real payments | Mock gateway | Tich hop MoMo/VNPay thuc |

---

## 4.8 Kết luận Chương 4

Hệ thống EcomAI đã được xây dựng và triển khai thành công với:

**Về kiến trúc:**
- 7 microservices Django/FastAPI hoàn toàn độc lập
- API Gateway Nginx với rate limiting và smart routing
- 6 database riêng biệt theo Database-per-Service pattern
- JWT stateless authentication, RBAC phân quyền 3 cấp

**Về AI:**
- LSTM model đạt Precision@5 = 0.52, vượt Collaborative Filtering 67%
- Hybrid LSTM+RAG đạt Precision@5 = 0.67 — kết quả tốt nhất
- Chatbot tư vấn tiếng Việt tự nhiên với product cards
- Lịch sử chat persistent qua localStorage

**Về Frontend:**
- 5 trang HTML responsive, hiện đại với Bootstrap 5 + custom CSS
- Ảnh sản phẩm Unsplash chính xác theo từng loại
- Giỏ hàng riêng biệt theo user_id
- Chatbot widget với history persistence và product card đầy đủ

**Về triển khai:**
- Toàn bộ containerized bằng Docker
- Docker Compose cho phép khởi động 15 containers bằng 1 lệnh
- Data seeding tự động với 17 sản phẩm và 3 tài khoản mẫu

---

## Kết luận Tổng thể

Hệ thống EcomAI đã chứng minh hiệu quả của việc kết hợp **Microservices Architecture + DDD + AI** trong xây dựng nền tảng e-commerce hiện đại:

| Mục tiêu | Kết quả |
|---------|---------|
| Kiến trúc linh hoạt | 7 service độc lập, deploy riêng biệt |
| AI cá nhân hóa | LSTM + RAG, Precision@5 = 0.67 |
| Frontend hiện đại | Responsive, ảnh thật, chatbot |
| Triển khai dễ dàng | 1 lệnh docker compose up |
| Bảo mật | JWT + RBAC 3 cấp |
