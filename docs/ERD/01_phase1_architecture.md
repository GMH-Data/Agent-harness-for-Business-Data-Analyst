# Mô Tả Bản Vẽ: Phase 1 - End-to-End Data Engineering Architecture

Bản vẽ [phase1_architecture.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/phase1_architecture.drawio.png) mô tả kiến trúc hạ tầng kỹ thuật và luồng đi của dữ liệu từ nguồn gốc (ClickHouse) cho đến kho dữ liệu (BigQuery) và quy trình CI/CD.

## 1. Các thành phần chính trong kiến trúc
Sơ đồ được chia làm 3 phân vùng chính tương ứng với các bước trong quy trình ELT:

1.  **Nguồn dữ liệu (Source Layer):**
    *   **ClickHouse Server:** Nơi lưu trữ nhật ký sự kiện người dùng (`user_event_tracking`) và dữ liệu cấu hình phần cứng laptop của đối tác.
2.  **Đơn vị điều phối (Orchestration & Ingestion):**
    *   **Apache Airflow (Local):** Chạy nhiệm vụ định kỳ hàng ngày để đồng bộ dữ liệu.
    *   **PyArrow RAM Buffer (In-memory stream):** Kỹ thuật trích xuất dữ liệu, nén Snappy Parquet trực tiếp trong bộ nhớ đệm RAM để tải trực tiếp lên BigQuery, loại bỏ hoàn toàn chi phí lưu trữ trên Google Cloud Storage (GCS).
3.  **Kho dữ liệu & Mô hình hoá (Data Warehouse Layer):**
    *   **Google BigQuery:** Sử dụng kiến trúc Medallion 3 lớp:
        *   `laplaptech_raw` (Bronze Layer): Dữ liệu thô vừa hạ cánh từ ClickHouse.
        *   `laplaptech_staging` (Silver Layer): Dữ liệu được làm sạch, bóc tách JSON và chuẩn hoá định dạng thời gian qua `dbt`.
        *   `laplaptech_hardware` & `laplaptech_marketing` (Gold Layer / Data Marts): Dữ liệu được tổng hợp sẵn sàng cho AI khai thác.
    *   **dbt (data build tool):** Chịu trách nhiệm biên dịch và chạy các mô hình biến đổi dữ liệu trong BigQuery.

## 2. Luồng di chuyển của dữ liệu (Data Flow)
1.  **Airflow** kích hoạt DAG `clickhouse_to_bigquery_bronze` định kỳ.
2.  DAG thực hiện truy vấn ClickHouse, nén dữ liệu qua luồng **PyArrow** và gọi BigQuery Load API để ghi đè/chèn dữ liệu vào các bảng RAW trong BigQuery.
3.  Ngay sau khi quá trình nạp RAW hoàn tất, Airflow kích hoạt lệnh `dbt run` để chuyển đổi dữ liệu từ Silver sang Gold.
4.  Quy trình code dbt và Airflow được bảo vệ chặt chẽ bởi **GitHub Actions (CI/CD)**: Tự động biên dịch thử (dbt compile) và kiểm tra lỗi cú pháp DAG (DagBag test) trên mỗi commit được push lên nhánh `main`.

---
*Xem sơ đồ trực quan tại: [phase1_architecture.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/phase1_architecture.drawio.png)*
