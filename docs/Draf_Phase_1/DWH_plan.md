## 1. TỔNG QUAN KIẾN TRÚC KHO DỮ LIỆU (MEDALLION ARCHITECTURE)

Hệ thống Laplaptech Data Platform được vận hành trên Google Cloud BigQuery, tuân thủ kiến trúc phân tầng Medallion với tiêu chí tối ưu hóa chi phí điện toán (0 USD Compute):

* **Bronze Layer (`laplaptech_raw`):** Lưu trữ nguyên bản 1:1 dữ liệu từ ClickHouse (`brand`, `cpu_model`, `gpu_model`, `laptop_model`, `laptop_benchmark_result`, `user_event_tracking`). Dữ liệu được nạp trực tiếp qua bộ đệm RAM để tránh chi phí lưu trữ trung gian.
* **Silver Layer (`laplaptech_staging`):** Sử dụng dbt để bóc tách các trường JSON phức tạp (`event_data` và `device`), ép chuẩn kiểu dữ liệu số và làm sạch, khử trùng (deduplication) các bản ghi benchmark.
* **Gold Layer (`laplaptech_marts`):** Tầng dữ liệu nghiệp vụ (Data Marts) đã được tinh chỉnh, cung cấp số liệu trực tiếp cho AI Agent và BI Dashboard.

---

## 2. CHIẾN LƯỢC MÔ HÌNH HÓA VÀ KỸ NGHỆ ĐẶC TRƯNG (DATA MODELING & FEATURE ENGINEERING)

Tầng Gold được chia làm 2 mô hình dữ liệu (Domain) chuyên biệt, tích hợp sẵn các đặc trưng (Features) để giảm thiểu sai sót khi AI sinh mã SQL:

### Domain 1: Hardware & Performance (Mô hình One Big Table - OBT)

* **Bảng đại diện:** `dim_laptops_obt`.
* **Bản chất:** Bảng phẳng gộp toàn bộ thông số kỹ thuật và điểm số benchmark của thiết bị. Đã được xử lý khử trùng (1 dòng = 1 mẫu laptop).
* **Feature Engineering (Đặc trưng tính sẵn):**
* *Features Suy hao:* Tỷ lệ duy trì hiệu năng pin của CPU và GPU.
* *Features Cơ động:* Điểm số di động (thời lượng pin chia cho trọng lượng).
* *Features Ngữ nghĩa (Text Chunks):* Gộp các trường `note`, `cpu_note`, `gpu_note`, và thông số kỹ thuật thành khối văn bản phục vụ RAG.


* **Mục đích cho Agent:** Cung cấp thông tin cấu hình, so sánh thiết bị. Tuyệt đối không cần sử dụng lệnh `JOIN` khi truy vấn bảng này.

### Domain 2: Clickstream & SEO (Mô hình Kimball Star Schema)

* **Bảng đại diện:** Fact `fct_user_event_tracking` liên kết với các bảng Dimensions (`dim_pages`, `dim_sessions`, `dim_devices`, `dim_traffic_sources`).
* **Bản chất:** Dữ liệu hành vi người dùng được băm khóa đại diện (`FARM_FINGERPRINT`), phân vùng (Partitioning) theo ngày và gom cụm (Clustering) để tối ưu tốc độ quét dữ liệu.
* **Feature Engineering (Đặc trưng tính sẵn):**
* *Features Phiên (Session):* Cờ `is_bounce_session` để nhận diện các phiên truy cập thoát trang ngay lập tức.
* *Features Trích xuất:* Bóc tách thông tin hệ điều hành (`os_name`), thiết bị (`device_type`), nguồn truy cập (`referrer`) từ dữ liệu JSON gốc.


* **Mục đích cho Agent:** Cung cấp dữ liệu phân tích lưu lượng, hành trình khách hàng và tỷ lệ chuyển đổi.

---

## 3. PHẠM VI KHAI THÁC NGHIỆP VỤ (EXPLOITATION SCOPE)

AI Agent và hệ thống Automation được phép khai thác kho dữ liệu vào 4 mục tiêu kinh doanh cốt lõi:

* **Tối ưu SEO Tự động (Programmatic SEO):** Khai thác tần suất xem chung (Co-viewing) từ log sự kiện để tự động xuất bản các trang Landing Page so sánh đối đầu (Auto VS Pages) và tiêm JSON-LD Schema. Cảnh báo tự động các URL có tỷ lệ thoát cao.
* **Tối ưu Trải nghiệm (UI/UX):** Đo lường thời lượng phiên và tỷ lệ thoát theo từng loại thiết bị, hệ điều hành để phát hiện các lỗi layout hoặc trải nghiệm kém.
* **Tư vấn Kinh tế Phần cứng (Hardware Economics):** Phân tích hiệu suất trên điện năng (Score/Watt) và gợi ý phần cứng tối ưu chi phí/hiệu năng cho người dùng cuối (B2C).
* **Báo cáo Xu hướng (Market Intelligence):** Phân tích sự dịch chuyển về trọng lượng laptop, dung lượng pin và điểm benchmark qua các năm để tạo báo cáo ngành tự động.

---

## 4. QUY TẮC ĐIỀU PHỐI (INTENT ROUTING RULES CHO AGENT)

> **Chỉ thị nghiêm ngặt dành cho LLM Router:** Dựa vào ý định của người dùng, Agent bắt buộc phải chọn đúng công cụ giao tiếp (MCP Tools):

1. **Intent "Truy vấn Thông số / Lọc Phần cứng":**
* *Công cụ:* `bigquery_sql_mcp_server`.
* *Hành động:* Truy vấn SQL duy nhất trên bảng `dim_laptops_obt`.


2. **Intent "Phân tích Traffic / Hành vi SEO":**
* *Công cụ:* `bigquery_sql_mcp_server`.
* *Hành động:* Truy vấn SQL trên `fct_user_event_tracking` kết hợp với các bảng `dim_*`.


3. **Intent "Hỏi đáp Cảm nhận / Trải nghiệm / Đánh giá chủ quan":**
* *Công cụ:* `hardware_rag_mcp_server`.
* *Hành động:* Tìm kiếm ngữ nghĩa (Vector Search) trên khối văn bản review và ghi chú cấu hình. Không dùng SQL cho số liệu toán học trong trường hợp này.


4. **Intent "Trực quan hóa Dữ liệu / Vẽ Biểu đồ":**
* *Công cụ:* `superset_mcp_tool`.
* *Hành động:* Tự động sinh cấu trúc JSON và tạo Dashboard-as-Code trên Apache Superset.

