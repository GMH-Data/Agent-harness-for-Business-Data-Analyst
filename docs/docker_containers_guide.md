# HƯỚNG DẪN TRUY CẬP CÁC DỊCH VỤ DOCKER STACK & CONTAINER (PHASE 2)

Tài liệu này tổng hợp toàn bộ các đường dẫn Web UI, thông tin kết nối và câu lệnh truy cập vào các container dịch vụ trong hạ tầng Docker Stack của dự án AI RISSER.

---

## 1. Qdrant Vector Database (Vector Search & Semantic Cache)

* **Dashboard Web UI (Qdrant Web Console)**:
  - Link: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
  *(Tại đây bạn có thể xem danh sách các Collections: `schema_metadata`, `analysis_memory`, thực hiện query vector và kiểm tra các payload/points trực quan)*.

* **REST API Endpoint**:
  - URL: `http://localhost:6333`
  - Kiểm tra trạng thái: `curl http://localhost:6333/healthz`
  - Kiểm tra các Collections: `curl http://localhost:6333/collections`

* **gRPC Endpoint**: `localhost:6334`

---

## 2. Apache Superset (Business Intelligence & Chart Dashboard)

* **Web UI**:
  - Link: [http://localhost:8088](http://localhost:8088)

* **Tài khoản đăng nhập mặc định (Local Sandbox)**:
  - **Username**: `admin`
  - **Password**: `admin`

* **Công dụng**:
  - Trực quan hóa các bảng Marketing Star Schema từ BigQuery.
  - Lấy link nhúng/xem nhanh cho AI Agent qua MCP Tool `get_dashboard_link`.

---

## 3. PostgreSQL (Metadata Repository)

* **Host**: `localhost`
* **Port**: `5432`
* **Database**: `superset` (hoặc `postgres`)
* **Username / Password**: `postgres` / `postgres`

---

## 4. CÁC CÂU LỆNH DOCKER THƯỜNG DÙNG

### 4.1. Xem danh sách các Container đang chạy:
```bash
docker ps
```

### 4.2. Kiểm tra Logs của Container cụ thể:
```bash
# Xem log Qdrant
docker logs -f ai_risser_qdrant

# Xem log Superset
docker logs -f ai_risser_superset
```

### 4.3. Truy cập vào bên trong Container (Bash/Shell):
```bash
# Vào container Qdrant
docker exec -it ai_risser_qdrant sh

# Vào container Superset
docker exec -it ai_risser_superset bash
```

### 4.4. Khởi động lại cụm Docker Stack:
```bash
cd "/home/gmh/Project/AI RISSER"
docker-compose down
docker-compose up -d
```
