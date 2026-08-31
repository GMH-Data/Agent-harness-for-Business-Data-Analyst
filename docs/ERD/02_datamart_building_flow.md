# Mô Tả Bản Vẽ: Phase 1 - Datamart Building Flow (Silver to Gold)

Bản vẽ [datamart_building_flow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/datamart_building_flow.drawio.png) mô tả chi tiết quy trình xử lý, làm sạch và mô hình hóa dữ liệu thông qua công cụ dbt bên trong Google BigQuery từ tầng Silver lên tầng Gold.

## 1. Tầng Staging (Silver Layer)
Dữ liệu thô từ tầng Raw chứa nhiều trường thông tin hỗn hợp và phức tạp. Ở tầng Silver, chúng tôi áp dụng các nghiệp vụ làm sạch sau:
*   **Deduplication (Loại bỏ trùng lặp):** Lọc bỏ các bản ghi benchmark laptop bị trùng cho cùng một dòng máy, chỉ giữ lại bản ghi có mốc cập nhật mới nhất.
*   **JSON Parsing (Giải mã JSON):** Tách trường `event_data` và `device` định dạng chuỗi phức tạp thành các cột tường minh như `url`, `referrer`, `os_name`, `device_type`, `browser` để AI dễ truy vấn.
*   **Time Standardization (Đồng nhất thời gian):** Đưa tất cả các trường thời gian từ định dạng nano giây của ClickHouse về kiểu dữ liệu `TIMESTAMP` chuẩn của BigQuery.

Các bảng Staging được tạo ra bao gồm:
*   `stg_brand`
*   `stg_cpu_model`
*   `stg_gpu_model`
*   `stg_laptop_model`
*   `stg_laptop_benchmark`
*   `stg_user_event_tracking`

## 2. Tầng Gold Layer (Data Marts)
Từ các bảng staging sạch, dbt tiến hành tổng hợp và join thành 2 cụm Domain chuyên biệt tối ưu cho AI RAG truy vấn:

### Cụm 1: Phần Cứng (Hardware Domain)
*   **`dim_laptops_obt` (One Big Table):** Gom toàn bộ thông tin cấu hình Laptop, thông tin CPU, GPU và điểm Benchmark tương ứng thành một bảng duy nhất để tránh việc AI phải sinh câu lệnh JOIN phức tạp.
*   **Các chỉ số ML-Ready (ML derived metrics):** Tính toán sẵn 4 chỉ số hiệu năng pin và điểm di động gồm: `cpu_single_battery_retention_pct`, `cpu_multi_battery_retention_pct`, `gpu_compute_battery_retention_pct` và `mobility_score`.

### Cụm 2: Tiếp Thị (Marketing Domain)
*   **`fct_user_event_tracking` (Fact Table):** Bảng sự kiện người dùng được phân vùng (`partitioned`) theo ngày `event_date` và nhóm cụm (`clustered`) theo `event_name` và `laptop_model_id` giúp tối ưu hóa chi phí quét dữ liệu của AI.
*   **Các bảng chiều (Dimension Tables):** 
    *   `dim_sessions`: Tính toán thời lượng phiên truy cập (`session_duration`) và gắn cờ phiên bị thoát (`is_bounce_session`).
    *   `dim_pages`: Băm khóa trang (`page_key`) bằng hàm `FARM_FINGERPRINT` dựa trên đường dẫn URL.
    *   `dim_devices`: Lưu trữ thông tin chi tiết về thiết bị và hệ điều hành của người dùng.

---
*Xem sơ đồ trực quan tại: [datamart_building_flow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/datamart_building_flow.drawio.png)*
