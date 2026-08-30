# Báo cáo Kết quả triển khai Phase 1: Hybrid Local Workflow

Tài liệu này tổng hợp toàn bộ kết quả thực thi thực tế của **Phase 1** để thiết lập kho dữ liệu nền tảng và luồng tự động hóa cho hệ thống AI RISSER.

## 1. Kết quả kiến trúc dữ liệu thô (Bronze Ingestion Layer)
* **Pipeline điều phối**: Thiết lập thành công Airflow DAG `clickhouse_to_bigquery_bronze` chạy hàng ngày lúc 01:00 AM UTC.
* **Cơ chế nạp trực tiếp qua RAM**: Dữ liệu từ ClickHouse đối tác (`applog.xomdata.com`) được nén Parquet (Snappy compression) trực tiếp trong RAM thông qua `pyarrow` và đẩy thẳng lên BigQuery. Đạt tiêu chuẩn **$0 Storage** (không dùng GCS làm bộ đệm).
* **Quản lý dữ liệu lớn**: Xử lý bảng log `user_event_tracking` (hơn 750,000 dòng) bằng phương pháp nạp tăng trưởng theo ngày (Incremental Load), được phân vùng (`Partitioned by event_date`) và ghi log kiểm toán qua phương thức **Batch Load** để vượt qua các giới hạn free tier của GCP.
* **Các bảng thô đã nạp trên GCP BigQuery (`laplaptech_raw`)**:
  - `raw_brand` (20 dòng)
  - `raw_cpu_model` (86 dòng)
  - `raw_gpu_model` (56 dòng)
  - `raw_laptop_model` (156 dòng)
  - `raw_laptop_benchmark_result` (152 dòng)
  - `raw_user_event_tracking` (Tăng trưởng ~1,000 dòng/ngày)
  - `audit_pipeline_logs` (Bảng lưu vết kiểm toán chạy pipeline)

---

## 2. Kết quả mô hình hóa dữ liệu (dbt Silver & Gold Layers)
Toàn bộ mã nguồn dbt models đã được biên dịch và chạy thành công trên BigQuery (`dbt run` đạt trạng thái `PASS=11` hoàn hảo).

### Tầng Staging (Silver Layer - `laplaptech_staging`)
* **Parse JSON**: Bóc tách dữ liệu string phức tạp từ `event_data` và `device` thành các trường thuộc tính tường minh (`url`, `referrer`, `os_name`, `device_type`...).
* **Khử trùng (Deduplication)**: Loại bỏ các bản ghi kiểm thử benchmark trùng lặp trên cùng một laptop, chỉ giữ lại bản ghi mới nhất dựa theo thời gian cập nhật.
* **Chuẩn hóa thời gian**: Đồng bộ toàn bộ dữ liệu timestamp nanosecond của ClickHouse sang định dạng timestamp chuẩn của BigQuery.

### Tầng Marts (Gold Layer - Tách biệt Domain)
Để AI Agent dễ dàng định tuyến ý định, Gold layer được chia thành 2 dataset độc lập:
1. **Dataset `laplaptech_hardware`**:
   - Bảng phẳng **`dim_laptops_obt`** (One Big Table) gộp toàn bộ cấu hình máy, CPU, GPU, Benchmark.
   - Tích hợp sẵn 4 chỉ số phái sinh: `cpu_single_battery_retention_pct`, `cpu_multi_battery_retention_pct`, `gpu_compute_battery_retention_pct`, và chỉ số di động `mobility_score`.
2. **Dataset `laplaptech_marketing`**:
   - Fact **`fct_user_event_tracking`** phân vùng theo ngày (`event_date`) và gom cụm (`Clustered by event_name, laptop_model_id`) để tối ưu hóa chi phí truy vấn SQL của AI Agent.
   - Các Dimension: **`dim_pages`** (URL băm `FARM_FINGERPRINT` tạo `page_key`), **`dim_devices`**, và **`dim_sessions`** (tính thời lượng và cờ `is_bounce_session`).

---

## 3. Tích hợp Orchestration và Tự động hóa CI/CD
* **Airflow + dbt Integration**: Thêm thành công task `dbt_run_transformations` (chạy qua `BashOperator`) vào cuối Airflow DAG. Luồng chạy tự động kích hoạt dbt ngay khi quá trình nạp dữ liệu thô kết thúc thành công.
* **Hạ tầng CI/CD (`.github/workflows/ci.yml`)**: Tích hợp GitHub Actions tự động kiểm thử cú pháp DAG (`DagBag` test) và dbt compilation (`dbt compile`) khi push/pull_request vào nhánh `main` để bảo vệ mã nguồn.

---

## 4. Trạng thái mã nguồn (Git Status)
Mã nguồn sạch, phân chia thư mục dbt models/macros khoa học, không sử dụng icons/emojis, đã commit an toàn vào nhánh `main`.
