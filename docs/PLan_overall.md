# KẾ HOẠCH TỔNG THỂ PHÁT TRIỂN HỆ THỐNG - AI RISSER

Hệ thống kho dữ liệu BigQuery & hệ sinh thái AI Agent toàn diện cho thương hiệu **Laplaptech**. Hệ thống xử lý dữ liệu từ ClickHouse đối tác, chuyển hóa qua dbt/BigQuery Medallion, cung cấp dữ liệu số liệu chính xác và tìm kiếm ngữ nghĩa (Hybrid Query-RAG) qua giao thức MCP cho LangGraph Agent, đóng gói thành ứng dụng kinh doanh tự động hóa (Streamlit, Programmatic SEO Engine, Superset Dashboard-as-Code).

---

## 1. Ma Trận Khái Niệm & Kế Hoạch Master (Master Concept Matrix)

| Tiêu chí | Phase 1: Building DWH & Data Marts (ĐÃ HOÀN THÀNH) | Phase 2: Harness, Hybrid RAG & Agent Core | Phase 3: Business App & AI Automation |
| :--- | :--- | :--- | :--- |
| **Mục tiêu cốt lõi** | Chuẩn hóa kho dữ liệu BigQuery Medallion, xử lý JSON phức tạp và dựng các Data Marts/Star Schema tối ưu. | Xây dựng Agentic AI Service với LangGraph, hệ thống MCP Tools, Hybrid RAG và Harness kiểm thử tự động. | Đóng gói sản phẩm kinh doanh (Streamlit App) tích hợp Cỗ máy SEO tự động và Live Log Streaming $0 Compute. |
| **Hạ tầng triển khai** | • Docker Containers (Airflow, Postgres)<br>• GCP BigQuery (US region) | • LangGraph Multi-Agent Engine<br>• LangSmith (Tracing & Prompt Hub)<br>• BigQuery Vector Search / Qdrant<br>• FastMCP SDK | • GCP Cloud Run (Streamlit App)<br>• GCP Artifact Registry (Docker Images)<br>• BigQuery BI Engine & Audit Logs |
| **Luồng dữ liệu (Data Flow)** | ClickHouse -> Airflow RAM (`io.BytesIO`) -> BQ Bronze -> dbt Silver -> Gold Marts | Gold Marts + Vector Index -> MCP Protocol -> LangGraph Router -> Tool Exec -> Response | Streamlit UI / User Events -> Live Console (UI) + Micro-batch Load Job -> `audit_logs` |
| **Kiến trúc Dữ liệu (Schemas)** | • `laplaptech_hardware.dim_laptops_obt`<br>• `laplaptech_marketing`: `fct_user_event_tracking`, `dim_pages`, `dim_sessions`, `dim_devices` | • Structured: SQL Query trên Gold Marts<br>• Unstructured: Vector Search trên Qdrant cho Schema Metadata & Semantic Cache | • `laplaptech_raw.audit_pipeline_logs`<br>• Programmatic VS Landing Page Schemas<br>• JSON-LD Structured Data Assets |
| **Bộ Công cụ (Tools & APIs)** | • Apache Airflow DAGs (Local stack)<br>• dbt Core (`dbt-bigquery`) | • `googleapis/mcp-toolbox` (BigQuery, Spanner, Cloud SQL)<br>• `superset_mcp_tool` (Dashboard-as-Code)<br>• `seo_co_viewing_mcp_server` | • Streamlit Web UI (Chat, Logs, Dashboards)<br>• Auto VS Page Generator<br>• JSON-LD Injector<br>• Bounce Rate Alert Trigger |
| **Kiểm soát Chất lượng (QA/Eval)** | • dbt compiler & Airflow DagBag test<br>• GitHub Actions CI/CD pipeline | • LangSmith: Execution Tracing & Latency<br>• DeepEval: Faithfulness >= 95%, Tool Acc >= 98er | • GitHub Actions CI/CD Pipeline<br>• Golden Dataset (100+ Test Cases)<br>• System Performance & Latency Monitor<br>• Micro-batch Ingestion Error Isolation |
| **Mô hình Chi phí (Cost)** | **$0** (Nạp RAM direct vào BigQuery Free Tier, dbt Core mã nguồn mở) | **Chi phí API LLM** (Vài cent khi chạy test harness và dev) | **$0 Compute** (Cloud Run Free Tier + BigQuery Micro-batch Load Job miễn phí) |

---

## 2. Chuyên Sâu Chi Tiết Theo Từng Phase

### PHASE 1: DATA ENGINEERING & DATA MARTS (TRẠNG THÁI: HOÀN THÀNH)

* **Bronze Layer (`laplaptech_raw`):** Lưu trữ 1:1 dữ liệu thô từ 6 bảng ClickHouse (`brand`, `cpu_model`, `gpu_model`, `laptop_model`, `laptop_benchmark_result`, `user_event_tracking`). Sử dụng cơ chế nạp direct từ RAM (`io.BytesIO`) để không phát sinh chi phí đĩa tạm.
* **Silver Layer (`laplaptech_staging`):** Sử dụng dbt để bóc tách 2 trường JSON phức tạp:
  * Từ `event_data`: Lấy `page_name`, `url`, `referrer`.
  * Từ `device`: Lấy `os_name`, `os_version`, `device_brand`, `device_type`, `device_name`.
  * Ép kiểu dữ liệu số (`FLOAT64`) cho TDP chip/GPU, kích thước màn hình, trọng lượng.
* **Gold Layer (Domain specific datasets):**
  * **Domain 1: Hardware & Performance (`laplaptech_hardware`)**:
    * `dim_laptops_obt`: One Big Table phẳng chứa thông số phần cứng, điểm Geekbench và tỷ lệ suy hao pin. Dùng để phân tích hiệu suất và thị hiếu kinh doanh.
  * **Domain 2: Marketing & Clickstream (`laplaptech_marketing`)**:
    * **Fact:** `fct_user_event_tracking` (PARTITION BY `event_date` (DAY), CLUSTER BY `event_name`, `laptop_model_id`).
    * **Dimensions:** `dim_pages` (băm `FARM_FINGERPRINT` tạo `page_key`), `dim_sessions`, `dim_devices`.
* **CI/CD Integration**: Tự động hóa kiểm thử Airflow DAG và dbt compilation qua GitHub Actions.

---

### PHASE 2: HARNESS, HYBRID RAG & AGENT CORE (TRẠNG THÁI: TIẾP THEO)

* **Hybrid Query-RAG Protocol:**
  * **Rule 1 (Number-Exact SQL):** Khi câu hỏi yêu cầu lọc thông số, tính trung bình, so sánh số liệu kinh doanh -> Gọi tool SQL (qua `googleapis/mcp-toolbox`) để query `dim_laptops_obt` hoặc `fct_user_event_tracking`.
  * **Rule 2 (Schema RAG):** Khi chuẩn bị viết SQL, sử dụng Semantic RAG trên `schema_metadata` để Agent tự tìm đúng cấu trúc bảng cần thiết trước khi sinh code.
* **Superset as an Agent MCP Tool:** Agent sử dụng `superset_mcp_tool` làm công cụ BI tự sinh Dashboard-as-Code.
* **LangGraph Flow:** 
  ```mermaid
  graph TD
      A[Intent Router] --> B[SQL/Tool Planner]
      B --> C[Tool Execution & Self-Correction]
      C -->|Tự sửa SQL/API nếu lỗi| B
      C --> D[Hybrid Synthesis & Response]
  ```
* **LangSmith & Harness:** Tích hợp LangSmith để trace log; chạy bộ kiểm thử 100+ Golden Test Cases qua DeepEval trên GitHub Actions.

---

### PHASE 3: BUSINESS APPLICATIONS & ENTERPRISE AI AUTOMATION

* **Streamlit Multi-tab Interface:**
  * **Tab 1 (Business Analytics Console):** Giao diện Chatbot B2B phân tích số liệu nội bộ (SQL + Superset).
  * **Tab 2 (Live Log Console):** Hiển thị dòng log chạy hệ thống theo thời gian thực.
  * **Tab 3 (Dashboard-as-Code):** Khung nhập liệu tự nhiên để Agent tự sinh dashboard Superset.
* **$0 Compute Logging Architecture:** Stream events tương tác Streamlit lên Console, buffer RAM và micro-batch load định kỳ vào BigQuery `audit_pipeline_logs` với $0 cước compute.
* **Autonomous Programmatic SEO Engine:**
  * Quét cặp máy co-viewing nhiều nhất từ `fct_user_event_tracking` để tự động xuất bản bài so sánh đối đầu (Auto VS Pages) kèm JSON-LD Schema.
  * Tự động quét các URL có tỷ lệ thoát cao để cập nhật lại nội dung.