# ĐÁNH GIÁ & PHẢN HỒI THEO TỪNG CHƯƠNG — ĐỀ TÀI "HỆ THỐNG E-COMMERCE MICROSERVICES (ECOMAI)"

> Cấu trúc: mỗi chương gồm (1) tự đánh giá cá nhân và (2) phản hồi của **10 người bạn** (mỗi người đều có ý kiến cho cả 4 chương, theo đúng chuyên môn của họ).

**Danh sách 10 người bạn tham gia đánh giá:**

| # | Tên | Chuyên môn |
|---|-----|-----------|
| 1 | Minh Tuấn | Backend (Java/Spring) |
| 2 | Thảo Nhi | Frontend (React) |
| 3 | Đức Anh | AI/ML |
| 4 | Phương Linh | QA/Testing |
| 5 | Quang Huy | DevOps |
| 6 | Hải Yến | Database |
| 7 | Nam Khánh | Security |
| 8 | Bảo Châu | Kinh tế (không chuyên IT) |
| 9 | Tiến Đạt | Mobile (Flutter) |
| 10 | Mỹ Hạnh | Quản lý dự án / SA&D |

---

## CHƯƠNG 1: TỪ MONOLITHIC ĐẾN MICROSERVICES VÀ DDD

### Tự đánh giá

Chương 1 đóng vai trò nền tảng lý thuyết, đi từ Monolithic → vấn đề gặp phải → Microservices → DDD. Điểm mạnh là có ví dụ thực tế (cấu trúc thư mục Django monolithic) giúp người đọc dễ liên hệ. Điểm yếu: phần so sánh Monolithic vs Microservices còn mang tính lý thuyết sách giáo khoa, chưa gắn trực tiếp với những khó khăn cụ thể mà nhóm gặp phải khi làm đồ án (vì đồ án làm microservices từ đầu, không thực sự "chuyển đổi" từ một bản monolithic có thật).

### Phản hồi từ 10 người bạn

1. **Minh Tuấn (Backend)**: "Sơ đồ kiến trúc Monolithic rõ ràng, dễ hiểu. Nhưng phần lý do 'tại sao tách' nên dẫn chứng bằng vấn đề cụ thể của hệ EcomAI (ví dụ: AI service cần PyTorch nặng, không nên chung container với Django) thay vì chỉ nói chung 'khó scale, khó maintain'."

2. **Thảo Nhi (Frontend)**: "Chương này tập trung backend là hợp lý vì đó là trọng tâm đồ án, nhưng có thể thêm 1-2 câu về việc frontend monolithic (1 SPA lớn) so với nhiều trang tĩnh tách biệt như EcomAI để phần lý thuyết bao quát hơn."

3. **Đức Anh (AI/ML)**: "Phần này chưa nhắc đến AI Service — hợp lý vì AI là phần mở rộng sau, nhưng nên có 1 câu dẫn dắt kiểu 'kiến trúc monolithic gần như không thể tích hợp một AI service nặng về tính toán', để chương 1 có cầu nối tự nhiên đến chương 3."

4. **Phương Linh (QA)**: "Một góc nhìn thiếu trong chương 1: monolithic dễ test hơn (1 codebase, 1 lần chạy test suite) còn microservices cần chiến lược test riêng (unit, contract test, integration). Đây là trade-off quan trọng nên được nêu ngay từ đầu vì ảnh hưởng đến toàn bộ đồ án sau này."

5. **Quang Huy (DevOps)**: "Phần triển khai (deployment) của Monolithic vs Microservices nên được nhấn mạnh hơn — ví dụ 1 server vs nhiều container — vì đây chính là điều chương 4 sẽ hiện thực hóa bằng 17 container. Hiện tại sơ đồ có nhưng thiếu liên kết 'tại sao việc này dẫn đến 17 container ở chương 4'."

6. **Hải Yến (Database)**: "Ví dụ monolithic dùng 'Single Shared Database' rất đúng, nhưng nên nói rõ hơn vấn đề cụ thể: khi 6 module dùng chung 1 DB, một migration sai ở module Product có thể làm sập luôn module Order — đây là động lực chính cho Database-per-Service ở chương 2."

7. **Nam Khánh (Security)**: "Góc bảo mật: monolithic có ưu điểm là dễ áp dụng 1 lớp authentication chung, còn microservices phải giải quyết bài toán xác thực phân tán (JWT, mỗi service tự verify). Chương 1 chưa đề cập điều này, nhưng nó chính là lý do JWT được chọn ở chương 2-4."

8. **Bảo Châu (Kinh tế)**: "Phần giải thích khái niệm rất dễ hiểu với người không chuyên, sơ đồ trực quan. Mình hiểu được vì sao 'một khối lớn' lại khó sửa hơn 'nhiều khối nhỏ' — ví dụ về thư mục Django giúp mình hình dung rõ hơn."

9. **Tiến Đạt (Mobile)**: "Từ góc độ client (mobile/frontend), monolithic thường nghĩa là 1 base URL API duy nhất, còn microservices qua gateway vẫn có thể trông giống 1 base URL nhờ API Gateway — chương 1 nên nói rõ điểm này để người đọc không nghĩ microservices nghĩa là client phải gọi 8 địa chỉ khác nhau."

10. **Mỹ Hạnh (PM/SA&D)**: "Về mặt trình bày, chương 1 làm tốt vai trò 'đặt vấn đề' cho toàn bộ tiểu luận — đi từ khái niệm quen thuộc (monolithic) đến khái niệm mới (DDD, bounded context) một cách tuần tự, hợp với cấu trúc một báo cáo SA&D. Góp ý duy nhất là nên có một đoạn kết ngắn tóm tắt 'những nguyên tắc nào từ chương 1 sẽ được áp dụng cụ thể ở chương 2' để tăng tính liên kết giữa các chương."

---

## CHƯƠNG 2: PHÁT TRIỂN HỆ E-COMMERCE MICROSERVICES (PHÂN TÍCH & THIẾT KẾ DDD)

### Tự đánh giá

Đây là chương mình tự tin nhất về mặt thiết kế: 11 functional requirements rõ ràng, bounded context ánh xạ 1-1 sang service, và đặc biệt là User Service áp dụng đúng DDD (Aggregate Root, Value Object, Entity). Class diagram và database schema cho 6 service + sequence diagram luồng mua hàng end-to-end giúp chương này có tính thực thi cao. Hạn chế: chỉ User Service được phân tích DDD sâu (Aggregate/VO/Entity), các service còn lại (Cart, Order, Payment, Shipping) thiết kế khá "CRUD thuần", chưa thấy rõ Aggregate Root hay Domain Event ở các service đó.

### Phản hồi từ 10 người bạn

1. **Minh Tuấn (Backend)**: "Thiết kế Order với 8 trạng thái và Payment với 5 phương thức/5 trạng thái khá đầy đủ cho một hệ thương mại điện tử. Tuy nhiên Order nên được xem là Aggregate Root chứa OrderItem, và việc chuyển trạng thái (pending → confirmed → ...) nên có validate transition rõ ràng (state machine), hiện tại class diagram chưa thể hiện ràng buộc này."

2. **Thảo Nhi (Frontend)**: "Cart Service với `total_price`/`total_items` là computed property rất tiện cho frontend hiển thị — điểm này tốt. Nhưng `CartItem` lưu `product_name`, `product_price`, `product_image` denormalized từ Product Service — nên nói rõ trong tài liệu cơ chế đồng bộ khi giá sản phẩm thay đổi (giá trong cart có cập nhật theo Product Service không?)."

3. **Đức Anh (AI/ML)**: "Chương 2 đặt nền cho chương 3 khá tốt qua việc đưa Redis và Neo4j vào sơ đồ data model tổng thể từ sớm. Tuy nhiên `UserBehaviorEvent` (bảng quan trọng cho AI) lại không xuất hiện trong class diagram Product Service ở mục 2.4 — nên bổ sung để người đọc thấy được sự liên kết giữa thiết kế DDD và pipeline AI ngay từ chương này."

4. **Phương Linh (QA)**: "Sequence diagram luồng mua hàng end-to-end (2.6.1) rất hữu ích — đây chính là 'happy path' nên được viết test integration đầu tiên. Activity diagram xử lý thanh toán (2.6.2) cũng nêu rõ các nhánh thành công/thất bại, nhưng tài liệu chưa nói service nào sẽ chịu trách nhiệm rollback nếu Payment thành công nhưng Shipping tạo lỗi — đây là edge case quan trọng cần test."

5. **Quang Huy (DevOps)**: "6 database riêng biệt (1 MySQL + 5 PostgreSQL) đúng chuẩn Database-per-Service, dễ container hóa từng phần. Góp ý: nên ghi chú thêm trong chương 2 là mỗi DB sẽ có volume riêng (sẽ thấy ở chương 4) để người đọc hiểu ngay từ thiết kế đã tính đến việc persist dữ liệu khi container restart."

6. **Hải Yến (Database)**: "Phần 2.7.2 so sánh MySQL vs PostgreSQL rất rõ ràng và có lý do thuyết phục (ENUM native cho User, JSONB cho Product specs). Một điểm cần lưu ý: `Electronics.specifications` là JSONB không có schema cố định — nên nói thêm về việc index các field JSON hay nào để tránh full scan khi filter theo specs (ví dụ filter theo RAM, dung lượng)."

7. **Nam Khánh (Security)**: "RBAC ở mục 2.3.3 phân quyền theo Admin/Staff/Customer khá rõ ràng và đủ cho phạm vi đồ án. Tuy nhiên bảng RBAC này được định nghĩa ở User Service, còn việc *thực thi* (enforce) lại nằm ở từng service riêng (Product, Order...) — chương 2 nên mô tả cơ chế các service khác kiểm tra `role` từ JWT claims như thế nào, vì đây là điểm dễ bị làm sai (mỗi service tự check không đồng nhất)."

8. **Bảo Châu (Kinh tế)**: "Phần class diagram và sơ đồ database khá kỹ thuật nên mình không đánh giá sâu được, nhưng đọc phần RBAC (bảng phân quyền Admin/Staff/Customer) thì rất dễ hiểu — giống như phân quyền nhân viên trong một công ty thực tế (ai được xem báo cáo, ai được sửa giá sản phẩm...)."

9. **Tiến Đạt (Mobile)**: "API endpoints ở mục 2.3.5 (`/auth/register/`, `/auth/login/`, `/auth/token/refresh/`...) là những endpoint cơ bản mà app mobile chắc chắn cần dùng. Điểm cần bổ sung: chưa thấy endpoint logout / revoke refresh token — với app mobile, việc người dùng đăng xuất trên 1 thiết bị nhưng token vẫn còn hạn ở thiết bị khác là vấn đề thực tế cần xử lý."

10. **Mỹ Hạnh (PM/SA&D)**: "Đây là chương có giá trị học thuật cao nhất xét theo môn SA&D: đi từ Functional/Non-functional Requirements → Use Case → Bounded Context → Class Diagram → Database Schema → Sequence Diagram, đúng trình tự phân tích thiết kế chuẩn. Góp ý: nên có một bảng traceability nhỏ map từ FR-01..FR-11 (mục 2.1.1) sang service tương ứng, để thấy rõ mọi yêu cầu đều được 'phủ' bởi thiết kế."

---

## CHƯƠNG 3: AI SERVICE CHO TƯ VẤN SẢN PHẨM

### Tự đánh giá

Chương 3 là phần đầu tư nhiều công sức nhất: huấn luyện và so sánh thực nghiệm RNN/LSTM/BiLSTM (chọn BiLSTM, F1-macro 0.5267), xây KB_Graph trên Neo4j, và Graph-RAG cho chatbot. Việc trình bày pipeline tổng thể (3.1.2) giúp người đọc thấy được luồng dữ liệu thật từ frontend → product-service → AI service. Hạn chế lớn nhất là dữ liệu huấn luyện (`data_user500.csv`) được sinh mô phỏng (`simulate_behavior`) theo persona giả định, nên kết quả F1 ~0.53 phản ánh dữ liệu giả nhiều hơn là hành vi người dùng thật.

### Phản hồi từ 10 người bạn

1. **Minh Tuấn (Backend)**: "Cơ chế ghi `user_behavior_log.csv` đồng thời với lưu DB (3.3.1) là một giải pháp pragmatic để chia sẻ dữ liệu giữa Django và FastAPI mà không cần message broker — phù hợp với quy mô đồ án. Nhưng về lâu dài, ghi file CSV từ nhiều request đồng thời (concurrent writes) có thể gây race condition/corrupt file mà tài liệu chưa đề cập."

2. **Thảo Nhi (Frontend)**: "Chatbot widget với lịch sử lưu localStorage (3.6.3) là điểm UX tốt. Tuy nhiên câu trả lời chatbot trả về text đã ghép sẵn (bao gồm cả `graph_note`) — nên cân nhắc tách `answer` và `graph_note` thành 2 trường riêng ở response để frontend linh hoạt hiển thị (ví dụ graph_note hiển thị dạng badge 'Gợi ý dành riêng cho bạn' khác màu)."

3. **Đức Anh (AI/ML)**: "Phần 3.2-3.4 làm bài bản: cùng kiến trúc cơ sở `SequenceClassifier`, cùng hyperparameter, so sánh fair giữa 3 model, có confusion matrix và training curves — đúng phương pháp thực nghiệm. Nhận xét ở 3.4.2 về overfitting (gap train/val) của LSTM/BiLSTM rất tốt, cho thấy hiểu bản chất chứ không chỉ chạy số. Góp ý: với dataset nhỏ (~350 mẫu train), nên thử thêm k-fold cross-validation để kết quả F1-macro đáng tin cậy hơn, vì chia 1 lần train/val/test với dữ liệu nhỏ dễ bị 'may rủi' theo cách chia."

4. **Phương Linh (QA)**: "Phần 3.7.3 (volume mount read-only cho AI service) là thiết kế tốt về tách biệt trách nhiệm. Nhưng toàn bộ chương 3 không có test nào cho pipeline AI: không test `build_context()` trả về đúng format khi KB_Graph trống, không test `/recommend` khi `model_best.pt` chưa tồn tại (lần đầu chạy). Đây là các edge case dễ gây lỗi 500 khi demo nếu thứ tự khởi động container không đúng."

5. **Quang Huy (DevOps)**: "Background refresh KB_Graph mỗi 120s (3.7.3) chạy bằng `asyncio.run_in_executor` trong cùng process với FastAPI — với CPU-only PyTorch, việc này có thể block event loop nếu KB_Graph lớn. Nên đo thời gian 1 lần refresh để xác nhận có ảnh hưởng đến response time của `/recommend`/`/chatbot` trong lúc refresh hay không."

6. **Hải Yến (Database)**: "KB_Graph trên Neo4j với các quan hệ VIEWED/CLICKED/ADDED_TO_CART/CO_OCCURS/PREDICTED_NEXT_ACTION (3.5.3) là một mô hình dữ liệu graph hợp lý cho bài toán gợi ý. Tuy nhiên tài liệu chưa nói về việc dọn dữ liệu cũ — nếu refresh liên tục mỗi 120s mà không xóa quan hệ PREDICTED_NEXT_ACTION cũ, graph sẽ phình to và chứa nhiều dự đoán lỗi thời cho cùng 1 user."

7. **Nam Khánh (Security)**: "`POST /graph/refresh` (3.7.3) là một endpoint có thể tốn tài nguyên (rebuild toàn bộ KB_Graph) — hiện tại không thấy đề cập việc endpoint này có cần xác thực admin hay không. Nếu để public, đây có thể là vector cho DoS đơn giản (gọi liên tục để CPU luôn bận rebuild graph)."

8. **Bảo Châu (Kinh tế)**: "Mình rất thích ví dụ chatbot trả lời 'tôi cần laptop gaming dưới 20 triệu' và gợi ý đúng sản phẩm kèm giá — phần này giải thích dễ hiểu cho người không chuyên: hệ thống 'nhớ' những gì mình từng xem để gợi ý đúng hơn. Câu trả lời tiếng Việt tự nhiên, không bị máy móc."

9. **Tiến Đạt (Mobile)**: "Response của `/chatbot` (3.6.4) trả về khá nhiều trường lồng nhau (`recommended_products`, `graph_context`, `sources`...) — với app mobile, càng nhiều trường thì càng cần models/DTO rõ ràng phía client. Nên có versioning cho API AI (`/v1/chatbot`) vì cấu trúc response này có khả năng thay đổi nhiều khi cải thiện model."

10. **Mỹ Hạnh (PM/SA&D)**: "Chương 3 là điểm nhấn khác biệt của đồ án so với một e-commerce thông thường — việc trình bày từ bài toán, kiến trúc model, dữ liệu, đến kết quả và tích hợp thực tế tạo thành một mạch hoàn chỉnh. Góp ý về trình bày: phần 3.4.1 (bảng kết quả) nên đặt ngay sau phần đặt vấn đề (3.2.1) trong một bản tóm tắt ở đầu chương — vì F1=0.53 là một con số mà hội đồng chắc chắn sẽ hỏi ngay, nên cần được 'đóng khung' bối cảnh (dataset nhỏ, mô phỏng) trước khi họ thấy số liệu."

---

## CHƯƠNG 4: XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

### Tự đánh giá

Chương 4 là chương "ráp tất cả lại": kiến trúc tổng thể 17 container, tech stack đầy đủ, cấu trúc code thật, nginx gateway, docker-compose, luồng JWT, API response mẫu cho từng luồng chính, và phần đánh giá ưu/nhược điểm + hướng cải thiện. Đây cũng là chương có giá trị "chứng minh" cao nhất vì show được hệ thống chạy thật (response JSON thật, không phải giả định). Hạn chế: phần 4.7.1 (hiệu năng ước tính) ghi rõ là "ước tính" — chưa có số liệu đo thật bằng công cụ load test (k6, JMeter, Locust), nên tính thuyết phục còn hạn chế.

### Phản hồi từ 10 người bạn

1. **Minh Tuấn (Backend)**: "Phần 4.3.1 (cấu trúc thư mục) cho thấy mỗi service đều theo đúng convention Django (models/serializers/views/urls/migrations) — nhất quán, dễ onboard người mới. Tuy nhiên các service Order/Payment/Shipping gọi nhau qua REST đồng bộ (`*_SERVICE_URL` trong docker-compose) — đúng như mình góp ý ở phần A trước đó, đây là điểm nghẽn nếu 1 trong các service downstream chậm."

2. **Thảo Nhi (Frontend)**: "10 trang HTML x 2 theme (4.8) hiển thị đẹp và đầy đủ luồng mua hàng. Phần `frontend/nginx.conf` proxy `/auth/`, `/products/`... sang gateway (4.3.1) giúp frontend gọi API cùng origin, tránh CORS — thiết kế hợp lý. Góp ý nhỏ: nên liệt kê rõ trong tài liệu cách đồng bộ giữa các file `*.html` và `*-dark.html` (ví dụ dùng script build hay sửa tay từng file?)."

3. **Đức Anh (AI/ML)**: "Response mẫu `/recommend` (4.6.4) thể hiện rõ chiến lược fallback: ưu tiên KB_Graph (BiLSTM), fallback LSTM demo khi chưa có dữ liệu — đây là thiết kế tốt cho 'cold start'. Phần 4.7.4 cũng tự nhận ra vấn đề cold-start và đề xuất hướng giải quyết (trending products + Graph-RAG mở rộng category) — cho thấy đồ án có tư duy đánh giá khách quan về hạn chế của chính mình."

4. **Phương Linh (QA)**: "Bảng 4.7.1 (hiệu năng ước tính) ghi rõ là ước tính, nên không nên dùng để kết luận hệ thống 'đạt yêu cầu < 200ms cho GET' như nêu ở chương 2 (Non-functional Requirements) — đây là điểm hội đồng dễ bắt lỗi: yêu cầu đặt ra ở chương 2 nhưng chương 4 chưa đo thật để xác nhận đạt hay không. Nên chạy ít nhất 1 lần load test đơn giản (ví dụ Apache Bench) cho `/products/` để có số liệu thật thay 'ước tính'."

5. **Quang Huy (DevOps)**: "docker-compose.yml (4.3.3) với healthcheck cho DB và `depends_on: condition: service_healthy` là thực hành tốt, tránh race condition khi service khởi động trước khi DB sẵn sàng. Tuy nhiên `command` của user-service/product-service chạy `migrate` + `seed` mỗi lần container start — nếu chạy lại `docker compose up` nhiều lần, cần đảm bảo các management command này idempotent (không tạo trùng dữ liệu seed)."

6. **Hải Yến (Database)**: "6 volume riêng cho 6 database (4.3.3, phần `volumes:`) đảm bảo dữ liệu persist qua các lần restart — đúng thực hành. Một câu hỏi đáng đặt ra cho phần 4.7: nếu cần backup, chiến lược backup cho 6 database + Neo4j riêng biệt là gì? Với 1 database trong monolithic, backup đơn giản hơn nhiều so với 6+1 database như hiện tại."

7. **Nam Khánh (Security)**: "Mục 4.4 (luồng JWT) trình bày rõ ràng access/refresh token. Tuy nhiên 4.5.3 công khai mật khẩu mặc định (`Admin@123`, `Staff@123`, `Customer@123`) và 4.3.3 dùng `password` cho mọi DB — với mục đích demo thì hợp lý, nhưng tài liệu nên có 1 dòng cảnh báo rõ 'đây là giá trị demo, không dùng cho production' để tránh hiểu nhầm khi hội đồng đọc."

8. **Bảo Châu (Kinh tế)**: "Phần 4.6 (API response mẫu) cho mình thấy hệ thống hoạt động thật — ví dụ response đăng nhập, danh sách sản phẩm, tạo đơn hàng đều có dữ liệu cụ thể (giá tiền, tracking code...) nên rất thuyết phục, không giống chỉ là bản vẽ trên giấy. Mục 4.8 tổng kết theo từng khía cạnh (kiến trúc, AI, frontend, triển khai) giúp người đọc không chuyên như mình dễ nắm được toàn bộ kết quả."

9. **Tiến Đạt (Mobile)**: "1 API Gateway duy nhất (port 80) cho toàn hệ thống (4.3.2) là điểm rất thuận lợi nếu sau này phát triển thêm app mobile — chỉ cần 1 base URL. Góp ý: nginx.conf hiện tại set `Access-Control-Allow-Origin *` (rất mở) — với mobile app thường không bị ảnh hưởng bởi CORS, nhưng nếu sau này có thêm web admin riêng domain khác, nên giới hạn origin cụ thể."

10. **Mỹ Hạnh (PM/SA&D)**: "Chương 4 hoàn thành tốt vai trò 'bằng chứng triển khai' — từ thiết kế (chương 2) đến hiện thực (chương 4) có sự nhất quán cao (ví dụ Order 8 trạng thái ở 2.5.2 khớp với mô tả ở 4.6.3). Mục 4.7.4 (nhược điểm và hướng cải thiện) là phần mình đánh giá cao nhất vì thể hiện tư duy phản biện — đúng tinh thần một báo cáo SA&D không chỉ trình bày 'cái đã làm' mà còn 'biết giới hạn của cái đã làm'. Để hoàn thiện, nên thêm bảng đối chiếu Non-functional Requirements (chương 2.1.2) với kết quả đạt được thực tế (chương 4.7) — hiện hai phần này chưa được liên kết trực tiếp."

---

## TỔNG HỢP CHUNG (4 CHƯƠNG)

| Chương | Điểm mạnh nổi bật | Góp ý chung được nhiều người nhắc |
|---|---|---|
| 1 | Lý thuyết dễ hiểu, sơ đồ trực quan | Cần liên kết rõ hơn với các vấn đề cụ thể sẽ giải quyết ở chương 2-4 |
| 2 | DDD áp dụng tốt cho User Service, đầy đủ class diagram/DB schema/sequence diagram | Áp dụng DDD (Aggregate/Domain Event) sâu hơn cho Order/Payment/Shipping; thêm traceability FR → service |
| 3 | So sánh thực nghiệm 3 model bài bản, Graph-RAG là điểm khác biệt | Dữ liệu mô phỏng nên được "đóng khung" rõ ngay từ đầu; thiếu test cho pipeline AI |
| 4 | Hệ thống chạy thật, response mẫu thuyết phục, tự đánh giá khách quan | Số liệu hiệu năng cần đo thật (không chỉ ước tính); đối chiếu lại với Non-functional Requirements ở chương 2 |

**Nhận xét tổng thể**: Cả 10 người bạn đều đánh giá đồ án có tính hoàn chỉnh cao (từ lý thuyết → thiết kế → AI → triển khai chạy thật), với điểm khác biệt rõ nhất là việc tích hợp AI (BiLSTM + KB_Graph + Graph-RAG) vào kiến trúc microservices. Các góp ý lặp lại nhiều nhất xoay quanh: (1) tăng tính liên kết giữa các chương (chương sau nên đối chiếu lại với yêu cầu/thiết kế ở chương trước), (2) bổ sung kiểm thử (cả cho service nghiệp vụ và pipeline AI), và (3) làm rõ ranh giới "giá trị demo" vs "production-ready" ở các phần liên quan đến bảo mật và hiệu năng.
