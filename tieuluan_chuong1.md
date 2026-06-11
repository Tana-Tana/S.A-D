# CHƯƠNG 1: TỪ MONOLITHIC ĐẾN MICROSERVICES VÀ DDD

---

## 1.1 Giới thiệu Monolithic Architecture

### 1.1.1 Khái niệm

**Monolithic Architecture** (kiến trúc nguyên khối) là mô hình phát triển phần mềm truyền thống, trong đó toàn bộ ứng dụng — bao gồm giao diện người dùng (Presentation Layer), logic nghiệp vụ (Business Logic Layer) và truy cập dữ liệu (Data Access Layer) — được đóng gói và triển khai như **một đơn vị duy nhất**. Tất cả thành phần chia sẻ cùng một tiến trình, cùng một codebase và thường dùng chung một cơ sở dữ liệu.

### 1.1.2 Cấu trúc điển hình — Sơ đồ Monolithic

```
+----------------------------------------------------------+
|              MONOLITHIC APPLICATION                      |
|                                                          |
|  +-------------------------------------------------+     |
|  |    Presentation Layer (UI / REST Controller)    |     |
|  +-----------------------+-------------------------+     |
|                          |                               |
|  +-----------------------v-------------------------+     |
|  |         Business Logic Layer                    |     |
|  |  ProductModule | UserModule | OrderModule |     |     |
|  |  PaymentModule | ShippingModule | CartModule    |     |
|  +-----------------------+-------------------------+     |
|                          |                               |
|  +-----------------------v-------------------------+     |
|  |        Data Access Layer (ORM / DAO)            |     |
|  +-----------------------+-------------------------+     |
|                          |                               |
|  +-----------------------v-------------------------+     |
|  |           Single Shared Database                |     |
|  |           (MySQL / PostgreSQL)                  |     |
|  +-------------------------------------------------+     |
+----------------------------------------------------------+
```

Hình 1.1: Kiến trúc Monolithic — tất cả module trong cùng một codebase và database

### 1.1.3 Ví dụ thực tế — E-Commerce Monolithic

Cấu trúc thư mục một hệ e-commerce monolithic điển hình (Django):

```
ecommerce_mono/
├── products/           # Quản lý sản phẩm
│   ├── models.py       # Product, Category, Review
│   ├── views.py        # ProductListView, ProductDetailView
│   └── urls.py
├── users/              # Quản lý người dùng
│   ├── models.py       # User, Profile, Address
│   └── views.py        # Register, Login, Profile
├── cart/               # Giỏ hàng
│   └── models.py       # Cart, CartItem
├── orders/             # Đặt hàng
│   └── models.py       # Order, OrderItem
├── payments/           # Thanh toán
│   └── models.py       # Payment, Transaction
├── shipping/           # Vận chuyển
│   └── models.py       # Shipment
├── settings.py         # Cấu hình chung — tất cả module
└── manage.py
```

Tất cả module dùng **cùng một database**, deploy **cùng một server**; sửa một chỗ có thể ảnh hưởng toàn bộ.

### 1.1.4 Nhược điểm chi tiết

| # | Vấn đề | Mô tả | Hậu quả thực tế |
|---|--------|-------|----------------|
| 1 | **Coupling cao** | Module phụ thuộc chặt nhau qua import trực tiếp | Sửa payment → có thể vỡ order, cart |
| 2 | **Scale toàn bộ** | Không thể scale riêng từng module | Module "Product" load cao cũng phải scale cả "User" |
| 3 | **Deploy rủi ro cao** | Deploy = triển khai toàn bộ app | Lỗi nhỏ trong 1 module → cả hệ thống down |
| 4 | **Tech lock-in** | Toàn bộ dùng một ngôn ngữ, framework | Không thể dùng Python cho AI trong khi phần còn lại dùng Java |
| 5 | **Khó onboard** | Codebase khổng lồ | Developer mới cần hiểu toàn bộ hệ thống trước khi làm việc |
| 6 | **Test chậm** | Phải test toàn bộ app | CI/CD pipeline mất hàng giờ |
| 7 | **Single point of failure** | Một bug = cả hệ thống down | SLA thấp, khó đạt 99.9% uptime |

### 1.1.5 Khi nào nên dùng Monolithic

Monolithic không phải lúc nào cũng tệ. Phù hợp với:
- **MVP (Minimum Viable Product)**: Ra mắt nhanh để kiểm chứng thị trường
- **Team nhỏ** (dưới 5-10 người): Chi phí điều phối thấp
- **Hệ thống đơn giản**: Logic nghiệp vụ chưa phức tạp
- **Giai đoạn đầu startup**: Tập trung vào tính năng, không phải hạ tầng

---

## 1.2 Microservices Architecture

### 1.2.1 Khái niệm và So sánh trực quan

**Microservices** là kiến trúc phân tách hệ thống thành các **dịch vụ nhỏ, độc lập**, mỗi service thực hiện một chức năng nghiệp vụ duy nhất, có database riêng, giao tiếp qua REST API và có thể deploy độc lập.

### 1.2.2 Sơ đồ so sánh Monolithic vs Microservices

```
MONOLITHIC                          MICROSERVICES
----------------------------        -----------------------------------------------
                                    
+---------------------+            +----------+   +-------------+   +----------+
|     Application     |            | User Svc |   | Product Svc |   | Cart Svc |
|  +---+ +---+ +---+  |            | :8000    |   | :8001       |   | :8002    |
|  |Usr| |Prd| |Ord|  |            | MySQL    |   | PostgreSQL  |   | Postgres |
|  +---+ +---+ +---+  |            +----------+   +-------------+   +----------+
|  +---+ +---+ +---+  |    
|  |Crt| |Pay| |Shp|  |   ===>    +----------+   +-------------+
|  +---+ +---+ +---+  |            | Order Svc|   | Payment Svc |
|     |              |             | :8003    |   | :8004       |
|  +--v-----------+  |            +----------+   +-------------+
|  |  Database    |  |            
|  +--------------+  |            +-------------+   +--------------+
+---------------------+            | Shipping Svc|   |  AI Service  |
                                   | :8005       |   |  :8006       |
  1 deploy / toan bo               +-------------+   | RNN/LSTM/    |
                                   |             |   | BiLSTM+Neo4j |
  Scale: toan bo app               |             |   +--------------+
  DB: dung chung                   +---> API Gateway (Nginx :80)
  Loi 1 = Down toan bo             
                                   Deploy doc lap tung service
                                   Scale: tung service theo nhu cau
                                   DB: moi service 1 DB rieng
                                   Loi 1 service != down he thong
```

Hình 1.2: So sánh trực quan Monolithic vs Microservices

### 1.2.3 Bảng so sánh chi tiết

| Tiêu chí | Monolithic | Microservices |
|----------|-----------|---------------|
| **Triển khai** | Một lần, toàn bộ app | Từng service độc lập |
| **Scale** | Scale toàn hệ thống | Scale riêng từng service |
| **Coupling** | Cao (tight coupling) | Thấp (loose coupling) |
| **Database** | Dùng chung 1 DB | Database-per-Service |
| **Ngôn ngữ/Framework** | Bị ràng buộc 1 stack | Tự do chọn (polyglot) |
| **Fault Isolation** | Lỗi 1 chỗ = sập toàn hệ | Lỗi 1 service, còn lại OK |
| **Team size phù hợp** | Nhỏ (< 10 người) | Lớn (nhiều team độc lập) |
| **Complexity vận hành** | Đơn giản | Phức tạp (cần DevOps) |
| **Debug/Trace** | Dễ, cùng process | Khó hơn, cần distributed tracing |
| **CI/CD** | Chậm (test toàn bộ) | Nhanh (test từng service) |
| **Time to market** | Nhanh ban đầu | Chậm ban đầu, nhanh về lâu dài |
| **Chi phí hạ tầng** | Thấp | Cao hơn (nhiều container/service) |

### 1.2.4 Big Tech và hành trình chuyển đổi sang Microservices

#### Netflix (2008 --> 2012)

Năm 2008: Hệ thống monolithic Oracle Database bị sự cố, **dịch vụ ngừng hoạt động 3 ngày liên tiếp**, gây thiệt hại hàng triệu USD và mất lòng tin khách hàng.

Từ 2009-2012: Bắt đầu "The Great Migration" — chuyển dần sang microservices trên AWS. Kết quả: hiện có **700+ microservices**, độ sẵn sàng **99.99%**, xử lý **200 triệu giờ xem phim/ngày**.

| Giai đoạn | Kiến trúc | Vấn đề |
|-----------|-----------|--------|
| 2007 | Monolithic + Oracle | Mở rộng kho DVD |
| 2008 | Sự cố database, 3 ngày downtime | Không thể scale |
| 2009 | Bắt đầu chuyển sang AWS Cloud | Migration bắt đầu |
| 2012 | Hoàn thành migration Microservices | 99.99% uptime |
| Nay | 700+ microservices | Chaos Engineering |

Sáng kiến đặc biệt: Phát minh **Chaos Engineering** (Netflix Simian Army) — cố tình gây lỗi ngẫu nhiên để kiểm thử độ bền của hệ thống phân tán.

#### Amazon (2001 --> 2004)

Vấn đề: Amazon.com monolith quá khổng lồ, team không thể làm việc độc lập, deploy một tính năng nhỏ mất nhiều ngày.

Giải pháp: CEO Jeff Bezos ban hành "API Mandate" — mọi team phải expose data qua API, không được gọi trực tiếp database của team khác.

Kết quả: Kiến trúc này trở thành nền tảng cho **AWS** — Amazon bán "infrastructure dư" của mình như một dịch vụ. **Two-Pizza Team**: Mỗi microservice do một team không quá 6-8 người quản lý (đủ ăn 2 pizza).

#### Uber (2014 --> 2016)

Vấn đề: Monolithic Node.js không scale kịp tốc độ tăng trưởng (từ 1 thành phố lên 70+ quốc gia trong 3 năm). Năm 2014 bắt đầu tách service đầu tiên — Trips service. Kết quả: Hiện có **2.200+ microservices**, xử lý **15 triệu chuyến xe/ngày**.

#### Shopify (2019 --> nay)

Vấn đề: Rails monolith ("the Majestic Monolith") đạt giới hạn — 300+ developer cùng commit vào một codebase. Giải pháp: "Shopify Pods" — chia monolith thành các module độc lập theo bounded context.

Bài học: Không phải cứ microservices là tốt — Shopify chọn **Modular Monolith** thay vì full microservices để tránh overhead vận hành.

### 1.2.5 Thiết kế Microservices khác Monolithic như thế nào?

| Khía cạnh | Monolithic | Microservices |
|-----------|-----------|---------------|
| **Giao tiếp module** | Gọi hàm trực tiếp (in-process) | HTTP REST / gRPC / Message Queue |
| **Xử lý lỗi** | Try-catch đơn giản | Circuit Breaker, Retry, Timeout |
| **Transaction** | ACID transaction DB | Saga Pattern, Eventual Consistency |
| **Logging** | Log tập trung 1 file | Distributed Logging (ELK Stack) |
| **Config** | 1 file settings.py | Mỗi service có config + env vars riêng |
| **Testing** | Unit + Integration test | Contract Test + Consumer-driven Test |
| **API Gateway** | Không cần | Bắt buộc (routing, auth, rate limit) |
| **Service discovery** | Không cần | Cần (Docker DNS / Consul / Kubernetes) |

---

## 1.3 Domain Driven Design (DDD)

### 1.3.1 Mục tiêu

**Domain Driven Design (DDD)** là phương pháp thiết kế phần mềm tập trung vào **business domain** (nghiệp vụ), đảm bảo mô hình phần mềm phản ánh đúng ngôn ngữ và quy trình kinh doanh thực tế.

Trong DDD, developer và domain expert dùng **Ubiquitous Language** — ngôn ngữ chung để mô tả hệ thống, tránh sự khác biệt giữa "ngôn ngữ kỹ thuật" và "ngôn ngữ kinh doanh".

### 1.3.2 Các khái niệm cốt lõi

**Entity** — Đối tượng có định danh (ID) duy nhất, tồn tại xuyên suốt vòng đời:
```python
class User(models.Model):
    id = models.BigAutoField(primary_key=True)   # dinh danh duy nhat
    username = models.CharField(max_length=150)
    role = models.CharField(max_length=20)
```

**Value Object** — Đối tượng không có ID, so sánh bằng giá trị, bất biến:
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = 'VND'
    # So sanh: Money(100000,'VND') == Money(100000,'VND') -> True
```

**Aggregate** — Nhóm các entity có liên kết chặt, truy cập qua Aggregate Root:
```python
class Order(models.Model):      # Aggregate Root
    user_id = models.IntegerField()
    total_price = models.DecimalField(...)

class OrderItem(models.Model):  # chi truy cap qua Order, khong truc tiep
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    quantity = models.IntegerField()
```

**Bounded Context** — Ranh giới rõ ràng của một domain, trong đó các khái niệm có nghĩa nhất định. Ví dụ: "User" trong User Context = authentication/profile; "User" trong Order Context = chỉ cần user_id.

**Domain Service** — Business logic không thuộc về Entity nào:
```python
class PriceCalculationService:
    def calculate_total(self, items, coupon=None):
        subtotal = sum(item.price * item.qty for item in items)
        discount = coupon.apply(subtotal) if coupon else 0
        return subtotal - discount
```

### 1.3.3 Context Map — Quan hệ giữa các Bounded Context

```
+----------------------+  Shared Kernel  +----------------------+
|    User Context      |<---(user_id)--->|   Order Context      |
|  - User Entity       |                 |  - Order Aggregate   |
|  - Role (RBAC)       |                 |  - OrderItem         |
|  - JWT Token         |                 |  - Status Machine    |
+----------------------+                 +----------------------+
           |                                         |
    Customer-Supplier                       Customer-Supplier
           |                                         |
           v                                         v
+----------------------+                 +----------------------+
|   Product Context    |                 |   Payment Context    |
|  - Product (base)    |                 |  - Payment Entity    |
|  - Book/Electronics  |                 |  - Transaction       |
|  - Fashion/Category  |                 |  - Gateway (MoMo..)  |
+----------------------+                 +----------------------+
           |                                         |
           +-------------------+---------------------+
                               |
                    +----------v-----------+
                    |     AI Context       |
                    |  - RNN/LSTM/BiLSTM   |
                    |  - KB_Graph (Neo4j)  |
                    |  - Graph-RAG Chatbot |
                    |  - Recommendation    |
                    +----------------------+
```

Hình 1.3: Context Map — mối quan hệ giữa các Bounded Context trong hệ thống EcomAI

Loại quan hệ:
- **Shared Kernel**: user_id được chia sẻ giữa các service (không share DB, chỉ share khái niệm)
- **Customer-Supplier**: Order service (customer) phụ thuộc Product service (supplier)
- **Anti-Corruption Layer**: AI service dùng ACL để chuẩn hóa dữ liệu từ Product

### 1.3.4 DDD trong Microservices

| Khái niệm DDD | Mapping trong hệ thống EcomAI |
|---------------|------------------------------|
| Bounded Context | 1 Microservice độc lập |
| Aggregate | Nhóm models trong 1 service |
| Domain Service | Service layer / management command Django |
| Repository | Django ORM QuerySet |
| Anti-Corruption Layer | Serializer / Adapter trong views.py |
| Ubiquitous Language | API contract (endpoint names, field names) |

---

## 1.4 Case Study: Hệ thống Quản lý Bệnh viện (Healthcare Demo)

### 1.4.1 Mô tả bài toán

Xây dựng hệ thống quản lý bệnh viện với 3 chức năng chính:
- Quản lý hồ sơ bệnh nhân (Patient Management)
- Quản lý thông tin bác sĩ và lịch làm việc (Doctor Management)
- Đặt và quản lý lịch khám bệnh (Appointment Scheduling)

### 1.4.2 Phân rã theo 4 bước DDD

**Bước 1: Xác định Domain**

| Domain | Chức năng cốt lõi | Entities chính |
|--------|------------------|----------------|
| Patient Management | Hồ sơ bệnh nhân, lịch sử khám | Patient, MedicalHistory |
| Doctor Management | Thông tin bác sĩ, lịch làm việc | Doctor, WorkSchedule |
| Appointment Scheduling | Đặt lịch, xác nhận, hủy | Appointment, TimeSlot |

**Bước 2: Xác định Bounded Context**

```
+---------------------+   Customer-Supplier   +----------------------+
|  Patient Context    |<---------------------->| Appointment Context  |
|                     |                        |                      |
| - PatientProfile    |   Customer-Supplier    | - Appointment        |
| - MedicalHistory    |<---------------------->| - TimeSlot           |
| - Prescription      |           ^            | - Notification       |
+---------------------+           |            +----------------------+
                                  |
                     +------------+
                     |
           +---------+----------+
           |   Doctor Context   |
           |                    |
           | - DoctorProfile    |
           | - WorkSchedule     |
           | - Specialization   |
           +--------------------+
```

**Bước 3: Phân rã thành 3 Microservices Django**

Patient Service — `patient_service/`

```python
# patients/models.py
class Patient(models.Model):
    """Ho so benh nhan — Entity chinh cua Patient Context"""
    full_name     = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender        = models.CharField(max_length=10,
                      choices=[('male','Nam'),('female','Nu')])
    phone         = models.CharField(max_length=15)
    blood_type    = models.CharField(max_length=5)
    address       = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patients'

class MedicalHistory(models.Model):
    """Lich su kham — Aggregate cua Patient"""
    patient      = models.ForeignKey(Patient, on_delete=models.CASCADE,
                     related_name='medical_histories')
    diagnosis    = models.TextField()
    treatment    = models.TextField()
    visit_date   = models.DateField()
    doctor_id    = models.IntegerField()  # ref sang Doctor Service
    prescription = models.TextField(blank=True)

    class Meta:
        db_table  = 'medical_histories'
        ordering  = ['-visit_date']
```

Doctor Service — `doctor_service/`

```python
# doctors/models.py
class Doctor(models.Model):
    """Thong tin bac si — Entity chinh cua Doctor Context"""
    SPECIALTY_CHOICES = (
        ('cardiology',  'Tim mach'),
        ('neurology',   'Than kinh'),
        ('pediatrics',  'Nhi khoa'),
        ('orthopedics', 'Chinh hinh'),
    )
    full_name      = models.CharField(max_length=200)
    specialty      = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    experience_yr  = models.IntegerField(default=0)
    is_available   = models.BooleanField(default=True)

    class Meta:
        db_table = 'doctors'

class WorkSchedule(models.Model):
    """Lich lam viec cua bac si"""
    doctor      = models.ForeignKey(Doctor, on_delete=models.CASCADE,
                    related_name='schedules')
    day_of_week = models.IntegerField()  # 0=Thu2, 6=CN
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    max_slots   = models.IntegerField(default=20)

    class Meta:
        db_table       = 'work_schedules'
        unique_together = ['doctor', 'day_of_week']
```

Appointment Service — `appointment_service/`

```python
# appointments/models.py
class Appointment(models.Model):
    """Lich hen kham — giao diem cua Patient + Doctor Context"""
    STATUS_CHOICES = (
        ('pending',   'Cho xac nhan'),
        ('confirmed', 'Da xac nhan'),
        ('completed', 'Da kham xong'),
        ('cancelled', 'Da huy'),
    )
    # Khong import Patient/Doctor model — chi luu ID
    patient_id     = models.IntegerField(db_index=True)
    doctor_id      = models.IntegerField(db_index=True)
    appointment_dt = models.DateTimeField()
    reason         = models.TextField()
    status         = models.CharField(max_length=20,
                       choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_dt']
```

**Bước 4: Xác định quan hệ và luồng API**

```
POST /appointments/
    |
    v
Appointment Service goi sang:
  GET http://patient-service:8010/patients/{patient_id}/
    -> Kiem tra benh nhan ton tai, lay thong tin
  GET http://doctor-service:8011/doctors/{doctor_id}/availability/
    -> Kiem tra bac si con lich trong khong
    |
    v
Neu hop le -> tao Appointment (status=pending)
Neu khong  -> tra ve loi cu the
```

| Service | Method | Endpoint | Mo ta |
|---------|--------|----------|-------|
| Patient | GET | `/patients/` | Danh sach benh nhan |
| Patient | POST | `/patients/` | Tao ho so moi |
| Patient | GET | `/patients/{id}/history/` | Lich su kham |
| Doctor | GET | `/doctors/` | Danh sach bac si |
| Doctor | GET | `/doctors/{id}/availability/` | Kiem tra lich trong |
| Appointment | POST | `/appointments/` | Dat lich hen |
| Appointment | PATCH | `/appointments/{id}/status/` | Cap nhat trang thai |

---

## 1.5 Ket luan Chuong 1

| Yeu to | Ket luan |
|--------|---------|
| **Monolithic** | Phu hop MVP, team nho, he thong don gian |
| **Microservices** | Phu hop he thong lon, team nhieu, scale cao |
| **DDD** | Nen tang bat buoc de phan ra dung bounded context |
| **Big Tech** | Netflix, Amazon, Uber deu chuyen sang Microservices sau khi scale lon |

Bai hoc quan trong: Microservices khong phai "silver bullet" — can bat dau tu Monolithic, khi he thong scale va team lon moi chuyen doi. DDD giup xac dinh khi nao va tach service nhu the nao la dung.

O cac chuong tiep theo, DDD va nguyen tac Microservices se duoc ap dung thuc te vao he thong E-Commerce voi 7 microservices + AI service.
