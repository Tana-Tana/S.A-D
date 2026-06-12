# CHƯƠNG 2: PHÁT TRIỂN HỆ E-COMMERCE MICROSERVICES

---

## 2.1 Phân tích Yêu cầu

### 2.1.1 Functional Requirements

| STT | Chức năng | Actor | Mô tả |
|-----|-----------|-------|-------|
| FR-01 | Đăng ký tài khoản | Customer | Tạo tài khoản với username, email, mật khẩu |
| FR-02 | Đăng nhập / JWT | Customer, Staff, Admin | Xác thực và nhận JWT token |
| FR-03 | Quản lý sản phẩm | Admin, Staff | CRUD sản phẩm đa loại (Book, Electronics, Fashion) |
| FR-04 | Tìm kiếm sản phẩm | Customer | Full-text search + filter theo loại, giá |
| FR-05 | Giỏ hàng | Customer | Thêm / sửa số lượng / xóa sản phẩm |
| FR-06 | Đặt hàng | Customer | Tạo order từ giỏ hàng, nhập địa chỉ giao |
| FR-07 | Thanh toán | Customer | COD, MoMo, VNPay, Chuyển khoản |
| FR-08 | Vận chuyển | Staff | Tạo đơn giao, theo dõi tracking |
| FR-09 | AI Gợi ý sản phẩm | Customer | LSTM recommendation dựa trên hành vi |
| FR-10 | Chatbot tư vấn | Customer | RAG chatbot trả lời câu hỏi về sản phẩm |
| FR-11 | Phân quyền RBAC | Admin | Admin / Staff / Customer với quyền khác nhau |

### 2.1.2 Non-functional Requirements

| Thuộc tính | Yêu cầu | Giải pháp áp dụng |
|-----------|---------|-------------------|
| **Scalability** | Scale từng service độc lập | Docker + Kubernetes-ready |
| **High Availability** | > 99% uptime | Health check, restart policy |
| **Security** | JWT + RBAC | djangorestframework-simplejwt |
| **Performance** | Response < 200ms cho GET | DB indexing, pagination |
| **Maintainability** | Mỗi service độc lập | DDD + Database-per-Service |
| **Portability** | Chạy trên mọi môi trường | Docker container hóa |

### 2.1.3 Use Case Diagram

```
                    +--------------------------------------------+
                    |         He thong EcomAI                    |
                    |                                            |
  +-----------+     |  [Dang ky / Dang nhap]                    |
  | Customer  |---->|  [Xem & Tim kiem san pham]                |
  +-----------+     |  [Them vao gio hang]                      |
                    |  [Dat hang & Thanh toan]                  |
                    |  [Xem goi y AI]                           |
                    |  [Chat voi AI tu van]                     |
                    |  [Theo doi don hang]                      |
                    |                                            |
  +-----------+     |  [Quan ly san pham (CRUD)]                |
  |  Staff    |---->|  [Xu ly don hang]                         |
  +-----------+     |  [Cap nhat van chuyen]                    |
                    |                                            |
  +-----------+     |  [Quan ly nguoi dung]                     |
  |  Admin    |---->|  [Xem bao cao he thong]                   |
  +-----------+     |  [Cau hinh he thong]                      |
                    +--------------------------------------------+
```

---

## 2.2 Phân rã hệ thống theo DDD

### 2.2.1 Bounded Context và Service Mapping

```
+-----------------------------------------------------------+
|                  BOUNDED CONTEXTS                         |
|                                                           |
|  +-------------+  +-------------+  +-------------+       |
|  | User Context|  |Product Ctx  |  | Cart Context|       |
|  |             |  |             |  |             |       |
|  | user-service|  |product-svc  |  | cart-service|       |
|  | Port: 8000  |  | Port: 8001  |  | Port: 8002  |       |
|  | DB: MySQL   |  | DB:Postgres |  | DB:Postgres |       |
|  +-------------+  +-------------+  +-------------+       |
|                                                           |
|  +-------------+  +-------------+  +-------------+       |
|  | Order Ctx   |  |Payment Ctx  |  |Shipping Ctx |       |
|  |             |  |             |  |             |       |
|  | order-svc   |  |payment-svc  |  |shipping-svc |       |
|  | Port: 8003  |  | Port: 8004  |  | Port: 8005  |       |
|  | DB:Postgres |  | DB:Postgres |  | DB:Postgres |       |
|  +-------------+  +-------------+  +-------------+       |
|                                                           |
|  +---------------------------+  +----------------------+ |
|  |        AI Context         |  |  Shared Infra        | |
|  |  ai-service                |  |  Redis (cache)      | |
|  |  Port: 8006                |  |  Neo4j (KB_Graph)   | |
|  |  FastAPI + PyTorch BiLSTM  |  |  Port: 6379 / 7474, | |
|  |  + KB_Graph + Graph-RAG    |  |  7687               | |
|  +---------------------------+  +----------------------+ |
+-----------------------------------------------------------+
                        |
              +---------v---------+
              |   API Gateway     |
              |   Nginx :80       |
              |   Rate Limiting   |
              |   JWT Validation  |
              +-------------------+
```

### 2.2.2 Nguyên tắc phân rã

- Mỗi Bounded Context = 1 Microservice độc lập
- Mỗi service có **database riêng** — không share DB
- Giao tiếp qua **REST API** qua API Gateway
- Không truy cập trực tiếp DB của service khác

---

## 2.3 Thiết kế User Service

### 2.3.1 Class Diagram — User Service

User Service được thiết kế theo DDD: **User** là Aggregate Root, **FullName** là Value Object (quan hệ 1-1), **Address** là Entity (quan hệ 1-N).

```
+----------------------------------------+      1:1      +----------------------+
|     User (extends AbstractUser)         |<------------->|   FullName (VO)      |
|     << Aggregate Root >>                |               +----------------------+
+----------------------------------------+               | + user: OneToOne(User)|
| + id: BigInt (PK)                       |               | + last_name: str      |
| + username: str (unique)                |               | + first_name: str     |
| + email: str                            |               +----------------------+
| + password: str (hashed)                |
| + role: enum [admin|staff|customer]     |      1:N      +----------------------+
| + phone: str (nullable)                 |<------------->|   Address (Entity)   |
| + avatar: url (nullable)                |               +----------------------+
| + is_active: bool                       |               | + user: FK(User)      |
| + created_at: datetime                  |               | + address_line: text  |
| + updated_at: datetime                  |               | + is_default: bool    |
+----------------------------------------+               | + created_at: datetime|
| + is_admin(): bool                      |               +----------------------+
| + is_staff_member(): bool               |
| + is_customer(): bool                   |
+----------------------------------------+
```

### 2.3.2 Django Implementation — User Model

```python
# user-service/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model với Role-Based Access Control (RBAC).
    Aggregate Root — extends AbstractUser để dùng authentication có sẵn của Django.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES,
                             default='customer', db_index=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_customer(self):
        return self.role == 'customer'


class FullName(models.Model):
    """Value Object — Họ và tên đầy đủ, quan hệ 1-1 với User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='full_name')
    last_name = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'user_full_names'


class Address(models.Model):
    """Entity — Địa chỉ của người dùng, quan hệ 1-N với User."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line = models.TextField()
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_addresses'
        ordering = ['-is_default', '-created_at']
```

### 2.3.3 Phân quyền RBAC

| Quyền | Admin | Staff | Customer |
|-------|:-----:|:-----:|:--------:|
| Xem sản phẩm | ✓ | ✓ | ✓ |
| Tạo/sửa sản phẩm | ✓ | ✓ | ✗ |
| Xóa sản phẩm | ✓ | ✗ | ✗ |
| Xem tất cả đơn hàng | ✓ | ✓ | ✗ |
| Xem đơn hàng của mình | ✓ | ✓ | ✓ |
| Xử lý đơn hàng | ✓ | ✓ | ✗ |
| Quản lý người dùng | ✓ | ✗ | ✗ |

### 2.3.4 Database Schema — User Service (MySQL)

```sql
CREATE TABLE users (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(150) NOT NULL UNIQUE,
    email       VARCHAR(254) NOT NULL,
    password    VARCHAR(255) NOT NULL,  -- hashed (PBKDF2)
    first_name  VARCHAR(150),           -- ke thua tu AbstractUser
    last_name   VARCHAR(150),           -- ke thua tu AbstractUser
    role        ENUM('admin','staff','customer') DEFAULT 'customer',
    phone       VARCHAR(15),
    avatar      VARCHAR(200),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_active (is_active)
);

-- Value Object: Ho ten day du (1-1 voi User)
CREATE TABLE user_full_names (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    last_name   VARCHAR(150),
    first_name  VARCHAR(150)
);

-- Entity: Dia chi (1-N voi User)
CREATE TABLE user_addresses (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_line TEXT NOT NULL,
    is_default   BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
);
```

**Lý do chọn MySQL**: Authentication workload đơn giản, hỗ trợ ENUM native, phổ biến và ổn định cho user data. Thiết kế tách `FullName` (Value Object) và `Address` (Entity) khỏi bảng `users` giúp tuân thủ nguyên tắc DDD — Aggregate Root chỉ chứa identity/role/credentials, các thuộc tính mô tả được tách thành VO/Entity riêng.

### 2.3.5 API Endpoints — User Service

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/auth/register/` | Đăng ký tài khoản mới | Không |
| POST | `/auth/login/` | Đăng nhập, nhận JWT | Không |
| POST | `/auth/token/refresh/` | Làm mới access token | Refresh token |
| GET | `/auth/verify/` | Xác thực token (nội bộ) | JWT |
| GET | `/users/` | Danh sách users (Admin) | Admin JWT |
| GET | `/users/{id}/` | Chi tiết user | JWT |

---

## 2.4 Thiết kế Product Service

### 2.4.1 Class Diagram — Product Service

```
+----------------------------------------------+
|               Product Service                |
|                                              |
|   +----------+  1     *  +----------------+ |
|   | Category |<----------| Product (base) | |
|   +----------+           +----------------+ |
|   | id       |           | id             | |
|   | name     |           | name           | |
|   | slug     |           | price          | |
|   | parent   | (FK self) | original_price | |
|   +----------+           | stock          | |
|                          | sold_count     | |
|                          | product_type   | |
|                          | image_url      | |
|                          | rating         | |
|                          | is_active      | |
|                          +-------+--------+ |
|                    1:1 extends|            |
|         +-----------+---------+----------+ |
|         |           |                    | |
|   +-----v---+  +----v------+  +----------v+ |
|   |  Book   |  |Electronics|  |  Fashion  | |
|   +---------+  +-----------+  +-----------+ |
|   | product |  | product   |  | product   | |
|   | author  |  | brand     |  | brand     | |
|   | isbn    |  | warranty  |  | size      | |
|   | pages   |  | specs JSON|  | color     | |
|   +---------+  +-----------+  | material  | |
|                               +-----------+ |
+----------------------------------------------+
```

### 2.4.2 Django Implementation — Product Models

```python
# product-service/products/models.py

class Category(models.Model):
    name   = models.CharField(max_length=100, unique=True)
    slug   = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True,
               on_delete=models.SET_NULL, related_name='children')

    class Meta:
        db_table = 'categories'

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('book', 'Sach'), ('electronics', 'Dien tu'),
        ('fashion', 'Thoi trang'), ('food', 'Thuc pham'),
        ('sports', 'The thao'), ('beauty', 'Lam dep'),
        ('furniture', 'Noi that'), ('other', 'Khac'),
    )
    name           = models.CharField(max_length=255, db_index=True)
    price          = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2,
                       null=True, blank=True)
    stock          = models.IntegerField(default=0)
    sold_count     = models.IntegerField(default=0)
    product_type   = models.CharField(max_length=20,
                       choices=PRODUCT_TYPE_CHOICES, db_index=True)
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL,
                       null=True, related_name='products')
    image_url      = models.URLField(blank=True, null=True)
    rating         = models.DecimalField(max_digits=3, decimal_places=2,
                       default=0.00)
    is_active      = models.BooleanField(default=True, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['product_type', 'is_active']),
        ]

class Book(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE,
                     related_name='book_detail')
    author       = models.CharField(max_length=255)
    publisher    = models.CharField(max_length=255, blank=True)
    isbn         = models.CharField(max_length=20, unique=True, null=True)
    pages        = models.IntegerField(null=True, blank=True)
    language     = models.CharField(max_length=50, default='Tieng Viet')

    class Meta:
        db_table = 'books'

class Electronics(models.Model):
    product         = models.OneToOneField(Product, on_delete=models.CASCADE,
                        related_name='electronics_detail')
    brand           = models.CharField(max_length=100)
    warranty_months = models.IntegerField(default=12)
    specifications  = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'electronics'

class Fashion(models.Model):
    product  = models.OneToOneField(Product, on_delete=models.CASCADE,
                 related_name='fashion_detail')
    brand    = models.CharField(max_length=100, blank=True)
    size     = models.CharField(max_length=10)
    color    = models.CharField(max_length=50)
    material = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'fashion'
```

### 2.4.3 Database Schema — Product Service (PostgreSQL)

```sql
-- Bang danh muc
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    parent_id   INT REFERENCES categories(id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Bang san pham chinh
CREATE TABLE products (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    price          NUMERIC(12,2) NOT NULL,
    original_price NUMERIC(12,2),
    stock          INT DEFAULT 0,
    sold_count     INT DEFAULT 0,
    product_type   VARCHAR(20) NOT NULL,
    category_id    INT REFERENCES categories(id) ON DELETE SET NULL,
    image_url      VARCHAR(500),
    rating         NUMERIC(3,2) DEFAULT 0.00,
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT NOW()
);

-- Bang chi tiet Sach
CREATE TABLE books (
    product_id  INT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    author      VARCHAR(255) NOT NULL,
    publisher   VARCHAR(255),
    isbn        VARCHAR(20) UNIQUE,
    pages       INT,
    language    VARCHAR(50) DEFAULT 'Tieng Viet'
);

-- Bang chi tiet Dien tu
CREATE TABLE electronics (
    product_id      INT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    brand           VARCHAR(100) NOT NULL,
    warranty_months INT DEFAULT 12,
    specifications  JSONB DEFAULT '{}'
);

-- Bang chi tiet Thoi trang
CREATE TABLE fashion (
    product_id  INT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    brand       VARCHAR(100),
    size        VARCHAR(10) NOT NULL,
    color       VARCHAR(50) NOT NULL,
    material    VARCHAR(100)
);
```

**Lý do chọn PostgreSQL**: Hỗ trợ JSONB mạnh (lưu specifications dạng JSON có thể index), quan hệ phức tạp (OneToOne với inheritance), full-text search tốt.

---

## 2.5 Thiết kế Cart, Order, Payment, Shipping Service

### 2.5.1 Class Diagram — Cart Service

```
+------------------+   1:N   +----------------------+
|      Cart        |-------->|       CartItem        |
+------------------+         +----------------------+
| id: BigInt       |         | id: BigInt           |
| user_id: Int     |         | cart: FK(Cart)       |
| created_at       |         | product_id: Int      |
| updated_at       |         | product_name: str    |
+------------------+         | product_price: dec   |
| total_price: prop|         | product_image: url   |
| total_items: prop|         | quantity: int        |
+------------------+         | subtotal: prop       |
                             +----------------------+
                             UNIQUE(cart, product_id)
```

### 2.5.2 Class Diagram — Order Service

```
+------------------------+   1:N   +-----------------------+
|         Order          |-------->|       OrderItem       |
+------------------------+         +-----------------------+
| id: BigInt             |         | id: BigInt            |
| user_id: Int           |         | order: FK(Order)      |
| total_price: Decimal   |         | product_id: Int       |
| shipping_address: Text |         | product_name: str     |
| shipping_fee: Decimal  |         | product_price: Decimal|
| status: enum           |         | quantity: Int         |
| note: Text             |         | subtotal: prop        |
| created_at: DateTime   |         +-----------------------+
+------------------------+
 Status: pending -> confirmed -> processing -> paid -> shipping -> delivered
         (co the chuyen sang) cancelled | refunded tu cac trang thai truoc do
```

### 2.5.3 Database Schema — Các Service còn lại

**Cart Service (PostgreSQL)**:
```sql
CREATE TABLE carts (
    id         BIGSERIAL PRIMARY KEY,
    user_id    INT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE cart_items (
    id            BIGSERIAL PRIMARY KEY,
    cart_id       INT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id    INT NOT NULL,
    product_name  VARCHAR(255) NOT NULL,
    product_price NUMERIC(12,2) NOT NULL,
    product_image VARCHAR(500),
    quantity      INT DEFAULT 1,
    added_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (cart_id, product_id)
);
```

**Order Service (PostgreSQL)**:
```sql
-- status: pending|confirmed|processing|paid|shipping|delivered|cancelled|refunded
CREATE TABLE orders (
    id               BIGSERIAL PRIMARY KEY,
    user_id          INT NOT NULL,
    total_price      NUMERIC(12,2) NOT NULL,
    shipping_address TEXT NOT NULL,
    shipping_fee     NUMERIC(10,2) DEFAULT 0,
    status           VARCHAR(20) DEFAULT 'pending',
    note             TEXT,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);
CREATE TABLE order_items (
    id            BIGSERIAL PRIMARY KEY,
    order_id      INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id    INT NOT NULL,
    product_name  VARCHAR(255) NOT NULL,
    product_price NUMERIC(12,2) NOT NULL,
    quantity      INT NOT NULL
);
```

**Payment Service (PostgreSQL)**:
```sql
-- method: cod|bank_transfer|momo|vnpay|zalopay
-- status: pending|processing|success|failed|refunded
CREATE TABLE payments (
    id               BIGSERIAL PRIMARY KEY,
    transaction_id   UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    order_id         INT NOT NULL,
    user_id          INT NOT NULL,
    amount           NUMERIC(12,2) NOT NULL,
    method           VARCHAR(20) DEFAULT 'cod',
    status           VARCHAR(20) DEFAULT 'pending',
    gateway_response JSONB DEFAULT '{}',
    paid_at          TIMESTAMP,
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);
```

**Shipping Service (PostgreSQL)**:
```sql
-- status: processing|picked_up|in_transit|out_for_delivery|delivered|failed|returned
CREATE TABLE shipments (
    id                BIGSERIAL PRIMARY KEY,
    order_id          INT NOT NULL UNIQUE,
    user_id           INT NOT NULL,
    tracking_code     VARCHAR(50) UNIQUE NOT NULL,
    address           TEXT NOT NULL,
    carrier           VARCHAR(100) DEFAULT 'GHN Express',
    status            VARCHAR(30) DEFAULT 'processing',
    estimated_delivery DATE,
    delivered_at      TIMESTAMP,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW()
);
CREATE TABLE shipment_history (
    id          BIGSERIAL PRIMARY KEY,
    shipment_id INT NOT NULL REFERENCES shipments(id),
    status      VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    location    VARCHAR(255),
    timestamp   TIMESTAMP DEFAULT NOW()
);
```

---

## 2.6 Luồng Hệ thống (Sequence Diagram)

### 2.6.1 Sequence Diagram — Luồng Mua hàng End-to-End

```
Customer   Gateway    User-Svc  Product-Svc  Cart-Svc  Order-Svc  Payment-Svc  Shipping-Svc
   |          |           |          |           |         |            |             |
   |--login-->|           |          |           |         |            |             |
   |          |--/auth/-->|          |           |         |            |             |
   |          |<--JWT-----|          |           |         |            |             |
   |<--JWT----|           |          |           |         |            |             |
   |          |           |          |           |         |            |             |
   |--GET /products/------|--------->|           |         |            |             |
   |<--product list-------|----------|           |         |            |             |
   |          |           |          |           |         |            |             |
   |--POST /cart/add/-----|----------|---------->|         |            |             |
   |          |           |          |<--verify--|         |            |             |
   |          |           |          |--stock OK>|         |            |             |
   |<--cart updated--------|----------|          |         |            |             |
   |          |           |          |           |         |            |             |
   |--POST /orders/create/------------|----------->|        |            |             |
   |          |           |          |           |<-cart---|            |             |
   |          |           |          |           |--data-->|            |             |
   |          |           |          |           |         |--create--> |             |
   |          |           |          |           |<-clear--|            |             |
   |<--order created (pending)--------|----------|---------|            |             |
   |          |           |          |           |         |            |             |
   |--POST /payment/pay/----|---------|-----------|---------|----------->|             |
   |          |           |          |           |         |<-paid------|             |
   |          |           |          |           |         |            |--create---->|
   |          |           |          |           |         |<-shipping--|             |
   |<--payment OK + tracking_code-----|----------|---------|------------|             |
```

### 2.6.2 Activity Diagram — Xử lý Thanh toán

```
[Bat dau] --> Nhan yeu cau thanh toan
                    |
            Kiem tra: da thanh toan chua?
           YES v            NO --> Return 400 "Da thanh toan"
      Tao Payment(status=processing)
                    |
       Goi Payment Gateway (MoMo/VNPay/COD)
                    |
            Gateway thanh cong?
        YES v           NO v
   status=success   status=failed
        |                |
   Goi Order Svc    Return 400
   status=paid
        |
   Goi Shipping Svc
   tao shipment
        |
   [Ket thuc] --> Return 201 payment info
```

---

## 2.7 Data Model tổng thể và Công nghệ Database

### 2.7.1 Biểu đồ Data Model toàn hệ thống

```
[User DB - MySQL]              [Product DB - PostgreSQL]
   users                           categories
    id, username, role              id, name, slug, parent_id
    password, phone, avatar        products
   user_full_names (1-1 VO)         id, name, price, stock
    user_id, last_name, first_name  product_type, category_id
   user_addresses (1-N Entity)      image_url, rating
    user_id, address_line,         books (product_id FK)
    is_default                     electronics (product_id FK)
                                   fashion (product_id FK)

[Cart DB - PostgreSQL]         [Order DB - PostgreSQL]
   carts                           orders
    id, user_id                     id, user_id, total_price
   cart_items                       status (8 trang thai), shipping_address
    cart_id FK, product_id          created_at, updated_at
    product_name, price            order_items
    quantity                        order_id FK, product_id
                                    product_name, price, qty

[Payment DB - PostgreSQL]      [Shipping DB - PostgreSQL]
   payments                        shipments
    id, transaction_id (UUID)       id, order_id (UNIQUE)
    order_id, user_id               tracking_code, carrier
    amount, method (5 loai)        status (7 trang thai)
    status (5 trang thai)          estimated_delivery, delivered_at
    gateway_response (JSONB)       shipment_history
    paid_at                         shipment_id FK
                                    status, description, location

[Redis - Cache]                [Neo4j - KB_Graph]
   cache key-value                 (User)-[:CO_OCCURS]->(Product)
   session/token cache             (User)-[:PREDICTED_NEXT_ACTION]->(Product)
                                    dung cho /recommend/graph, Graph-RAG
```

### 2.7.2 So sánh MySQL vs PostgreSQL

| Tiêu chí | MySQL (User Service) | PostgreSQL (Product, Order...) |
|----------|---------------------|-------------------------------|
| **Lý do chọn** | Authentication đơn giản | Cần JSONB, quan hệ phức tạp |
| **JSON support** | Cơ bản (JSON type) | Mạnh mẽ (JSONB + index on JSON) |
| **ENUM type** | Native ENUM | Dùng CHECK constraint |
| **Full-text search** | Cơ bản | Tốt hơn (tsvector, tsquery) |
| **Performance** | Đọc đơn giản nhanh | Tổng thể tốt hơn cho phức tạp |
| **Phù hợp cho** | User data, authentication | Product specs, order management |

---

## 2.8 Kết luận Chương 2

Hệ thống E-Commerce đã được thiết kế theo nguyên tắc DDD với:
- **6 microservices Django** (user, product, cart, order, payment, shipping) + **1 AI Service FastAPI**, mỗi service một database riêng
- **6 databases** (1 MySQL + 5 PostgreSQL) theo mô hình Database-per-Service, bổ sung **Redis** (cache) và **Neo4j** (KB_Graph) làm hạ tầng dùng chung
- **User Service** áp dụng DDD đầy đủ: User là Aggregate Root, FullName là Value Object (1-1), Address là Entity (1-N)
- **Class diagrams** rõ ràng cho từng service, đầy đủ enum trạng thái (Order 8 trạng thái, Payment 5 phương thức/5 trạng thái, Shipment 7 trạng thái)
- **Sequence diagram** thể hiện luồng mua hàng end-to-end
- **Django** xây dựng nhanh, ORM mạnh, phù hợp cho từng service CRUD; **FastAPI** cho AI Service cần hiệu năng ML cao

DDD giúp thiết kế đúng ranh giới service ngay từ đầu, tránh anti-pattern "monolith disguised as microservices".
