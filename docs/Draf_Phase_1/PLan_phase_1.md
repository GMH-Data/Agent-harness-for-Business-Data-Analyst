# KẾ HOẠCH TRIỂN KHAI PHASE 1: HYBRID LOCAL WORKFLOW (ĐÃ HOÀN THÀNH)

### Data Engineering & Data Marts (Local Compute & Orchestration -> BigQuery Cloud Storage)

---

## 1. TỔNG QUAN CHIẾN LƯỢC HYBRID LOCAL (STRATEGY & ARCHITECTURE)

* **Local Machine (VS Code + Docker):** Chịu trách nhiệm thực thi mã nguồn Python Ingestion, chạy Airflow Scheduler/Webserver và điều phối lệnh chuyển đổi dbt.
* **Google Cloud Platform (BigQuery Sandbox - $0 Free Tier):** Đóng vai trò là kho lưu trữ và xử lý truy vấn phân tầng (Bronze -> Silver -> Gold) theo đúng chuẩn cú pháp SQL BigQuery (`JSON_VALUE`, `FARM_FINGERPRINT`, `SAFE_DIVIDE`, `TIMESTAMP_SECONDS`).
* **Lợi ích cốt lõi:** Viết SQL dbt một lần duy nhất theo chuẩn BigQuery, kiểm thử toàn bộ luồng trên máy cá nhân, sau đó đóng gói đẩy lên GCP chạy ngay mà **không cần chỉnh sửa dù chỉ 1 dòng code SQL**.

```
========================================================================================================================
                                       HYBRID LOCAL ARCHITECTURE (PHASE 1)
========================================================================================================================

  [ MÔI TRƯỜNG LOCAL / VS CODE (MÁY BẠN) ]                                [ GOOGLE CLOUD BIGQUERY ($0 FREE TIER) ]
  ┌────────────────────────────────────────────────────────┐             ┌──────────────────────────────────────────────┐
  │ 1. Terminal / Python .venv:                            │             │ BRONZE LAYER (laplaptech_raw)                │
  │    • Chạy test Ingestion Python (test_ingest.py)       │             │ ├── raw_brand, raw_laptops, raw_benchmarks   │
  │    • Chạy trực tiếp dbt models (dbt run, dbt test)     │             │ ├── raw_user_event_tracking                  │
  │                                                        │             │ └── audit_pipeline_logs                      │
  │ 2. Docker Engine (docker-compose.yml):                 │             └──────────────────────┬───────────────────────┘
  │    • Airflow Webserver (http://localhost:8080)         │                                    │
  │    • Airflow Scheduler (Trigger DAG E2E)               │                                    │ (dbt run staging)
  │    • Containerized dbt execution                       │                                    ▼
  └──────────────────────────┬─────────────────────────────┘             ┌──────────────────────────────────────────────┐
                             │                                           │ SILVER LAYER (laplaptech_staging)            │
                             │ (1) Ingest via RAM (io.BytesIO)           │ ├── stg_user_events (Unnested JSON)          │
                             │ (2) Push dbt SQL execution jobs           │ └── stg_laplaptech__laptops, benchmarks,...  │
                             ▼                                           └──────────────────────┬───────────────────────┘
  ┌────────────────────────────────────────────────────────┐                                    │
  │ NGUỒN DỮ LIỆU ĐỐI TÁC:                                 │                                    │ (dbt run marts)
  │ ClickHouse Remote DB (applog.xomdata.com)              │                                    ▼
  │ • 5 Bảng danh mục / specs / benchmarks                 │             ┌──────────────────────────────────────────────┐
  │ • 1 Bảng user_event_tracking (Clickstream log)         │             │ GOLD LAYER (Custom Domain Datasets)          │
  │└───────────────────────────────────────────────────────┘             │ ├── laplaptech_hardware.dim_laptops_obt      │
                                                                         │ └── laplaptech_marketing:                    │
                                                                         │     fct_user_event_tracking, dim_pages,      │
                                                                         │     dim_sessions, dim_devices                │
                                                                         └──────────────────────────────────────────────┘
========================================================================================================================
```

---

## 2. QUY TRÌNH CHUYỂN DỊCH TỪNG STEP (STEP-BY-STEP TRANSITION FLOW)

Kế hoạch Phase 1 Hybrid Local được chia thành **5 Step tuần tự**:

```text
┌─────────────────────────────────────────┐
│ STEP 1: LOCAL SETUP & GCP AUTH          │ ── Khởi tạo Docker Airflow Stack, mount Keyfile và profiles.yml
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ STEP 2: BRONZE LAYER INGESTION          │ ── Ingestion DAG kéo 6 bảng từ ClickHouse qua RAM nạp vào BigQuery Bronze
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ STEP 3: LOCAL DBT MODELING (DEV SPEED)  │ ── Viết & test dbt Staging (parse JSON), Gold Hardware OBT & Marketing
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ STEP 4: ORCHESTRATION INTEGRATION       │ ── Tích hợp dbt run tự động trực tiếp vào Airflow DAG sau ingestion
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ STEP 5: AUTOMATION & CI/CD VERIFICATION │ ── Cài đặt CI/CD GitHub Actions kiểm thử DAG syntax và dbt compile
└─────────────────────────────────────────┘
```

---

## 3. CHI TIẾT TỪNG STEP THỰC THI (INPUT -> TASKS -> OUTPUT)

---

### STEP 1: KHỞI TẠO LOCAL DEV ENVIRONMENT, THIẾT LẬP DOCKER CONTAINER VÀ KẾT NỐI GCP BIGQUERY

* **Mục tiêu:** Thiết lập môi trường lập trình chuẩn trên máy, dựng sẵn hệ thống Docker (Airflow & dbt container) và liên kết dbt với BigQuery cloud ngay từ đầu.
* **Input:** Google Cloud Console, Service Account Key, Docker Engine.
* **Các công việc đã hoàn thành:**
1. **Dựng môi trường Docker Container cục bộ:**
   * Tạo file `Dockerfile` cho Airflow tích hợp sẵn `dbt-bigquery`, `clickhouse-connect`, `pyarrow`, `pandas`.
   * Tạo file `docker-compose.yml` khởi chạy cụm dịch vụ: Airflow Webserver, Airflow Scheduler, và Postgres làm Database metadata.
   * Cấu hình mount volume kết nối mã nguồn nội bộ: thư mục `./airflow/dags`, `./dbt`, `./Key` (chứa keyfile BigQuery).
2. **Cấu hình dbt & Profiles:**
   * Khởi tạo file `dbt/dbt_project.yml` và kết nối với BigQuery thông qua `dbt/profiles.yml` trỏ tới `/opt/airflow/Key/gcp_key.json` bên trong container.
   * Chạy thử lệnh dbt debug bên trong container thành công (`All checks passed!`).

---

### STEP 2: BRONZE LAYER INGESTION (AIRFLOW AUTOMATION)

* **Mục tiêu:** Thiết lập kết nối ClickHouse và cơ chế nén Parquet in-RAM nạp thẳng vào BigQuery Bronze không tạo tệp tạm.
* **Các công việc đã hoàn thành:**
1. Viết mã nguồn Ingestion trực tiếp vào Airflow DAG.
2. Thiết lập cơ chế tải:
   * **Full Refresh** cho 5 bảng danh mục cấu hình.
   * **Incremental Load** (Phân vùng theo ngày) cho bảng log lớn `user_event_tracking` dựa trên cột `event_date`.
3. Xử lý giới hạn GCP Free Tier sandbox bằng cách sử dụng **Batch Load** thay thế cho Streaming Insert để ghi vết audit log vào bảng `audit_pipeline_logs`.

---

### STEP 3: PHÁT TRIỂN & TEST TRỰC TIẾP DBT MODELS (SILVER & GOLD)

* **Mục tiêu:** Xử lý triệt để 2 trường JSON phức tạp và mô hình hóa thành 2 Data Marts tương ứng với 2 domain độc lập.
* **Các công việc đã hoàn thành:**
1. **Staging / Silver Layer (`models/silver/`):**
   * Viết `stg_laplaptech__user_events.sql` dùng `JSON_VALUE()` bóc tách các trường từ JSON `event_data` và `device`.
   * Khử trùng dữ liệu benchmark của cùng một `laptop_model_id` chỉ giữ lại bản ghi mới nhất.
   * Chuẩn hóa múi giờ và chuyển đổi an toàn kiểu nanosecond timestamp của ClickHouse thành timestamp chuẩn của BigQuery.
2. **Marts / Gold Layer (`models/gold/`):**
   * **Domain 1: Hardware & Performance (`laplaptech_hardware.dim_laptops_obt`)**: Bảng phẳng cấu hình phần cứng tích hợp sẵn tỷ lệ duy trì hiệu năng pin, chỉ số di động `mobility_score`, và gộp metadata review `semantic_text_chunk` cho RAG.
   * **Domain 2: Marketing & Clickstream (`laplaptech_marketing`)**: Gồm Fact `fct_user_event_tracking` (Partition theo `event_date` (DAY), Cluster theo `event_name`, `laptop_model_id`) kết nối với các Dimensions `dim_devices`, `dim_pages`, `dim_sessions`.

---

### STEP 4: ORCHESTRATION INTEGRATION (AIRFLOW + dbt)

* **Mục tiêu:** Tự động hóa hoàn toàn quy trình xử lý dữ liệu khép kín.
* **Các công việc đã hoàn thành:**
1. Cấu hình task `dbt_run_transformations` (sử dụng `BashOperator`) vào cuối Airflow DAG.
2. Thiết lập quan hệ phụ thuộc: Lệnh dbt chỉ được kích hoạt khi toàn bộ 6 task kéo dữ liệu thô (Bronze Ingestion) hoàn thành thành công.
3. Chạy test thử liên thông thành công, ghi nhận dbt tạo và cập nhật bảng đích ổn định trên BigQuery.

---

### STEP 5: AUTOMATION & CI/CD VERIFICATION

* **Mục tiêu:** Kiểm thử chất lượng và tự động hóa CI/CD thông qua Git.
* **Các công việc đã hoàn thành:**
1. Thiết lập file workflow `.github/workflows/ci.yml` trên GitHub Actions.
2. Tự động kiểm thử cú pháp mã nguồn Python Airflow DAG và cú pháp dbt compile mỗi lần có push/pull_request vào nhánh `main`.

---

## 4. MA TRẬN TỔNG KẾT PHASE 1 (HYBRID LOCAL)

| Hạng mục | Môi trường chạy | Công nghệ sử dụng | Chi phí phát sinh | Trạng thái |
| --- | --- | --- | --- | --- |
| **Orchestration & UI** | Docker Local (Máy bạn) | Apache Airflow 2.9+ (Postgres metadata) | **$0** | HOÀN THÀNH |
| **Ingestion Engine** | Local Container | Python 3.10, `clickhouse-connect`, `pyarrow` | **$0** | HOÀN THÀNH |
| **Transformation (Dev & Run)** | Local VS Code / Container | `dbt-bigquery` Core | **$0** | HOÀN THÀNH |
| **Data Warehouse (Storage)** | Google Cloud (Cloud) | BigQuery Datasets (Bronze, Silver, Gold) | **$0** (Free Tier GCP) | HOÀN THÀNH |
| **Audit & Lineage** | BigQuery Tables | `audit_pipeline_logs` & dbt Docs | **$0** | HOÀN THÀNH |