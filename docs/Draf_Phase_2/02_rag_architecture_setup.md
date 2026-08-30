# KẾ HOẠCH KIẾN TRÚC RAG (TRI-COLLECTION RAG)

## 1. Giới thiệu
Để tối ưu hóa chi phí Token LLM, giữ vững logic hội thoại dài hạn và giúp LLM truy xuất chính xác cấu trúc dữ liệu, hệ thống sử dụng **Kiến trúc RAG 3 Bảng (Tri-Collection RAG)** trên **Qdrant Cloud**.

## 2. Chi tiết 3 Collections

### 2.1. Collection 1: `schema_metadata`
* **Mục đích**: Cung cấp cấu trúc của các bảng trong Data Mart (Schema RAG) cho Agent (đặc biệt là SQL Agent) để sinh code SQL chính xác.
* **Cơ chế nạp (Ingestion)**: 
  - Không sử dụng phương pháp chia nhỏ văn bản (No chunking).
  - Trích xuất thông tin từ file cấu hình `dbt/models/gold/schema.yml`.
  - Chuyển đổi thành JSON Payload (bao gồm tên bảng, cột, kiểu dữ liệu, quan hệ).
  - Embedded vector được sinh ra từ "tóm tắt" bảng để phục vụ tìm kiếm. Khi truy xuất, LLM nhận lại toàn bộ cấu trúc JSON.

### 2.2. Collection 2: `validated_reports`
* **Mục đích**: Đóng vai trò là Semantic Cache (Bộ nhớ đệm ngữ nghĩa) nhằm tái sử dụng các kết quả đã được con người duyệt.
* **Cơ chế hoạt động**:
  - Khi người dùng đặt câu hỏi, Agent tìm trong Cache.
  - Nếu câu hỏi có độ tương đồng (Similarity) cao (> 95%), hệ thống lập tức trả về câu lệnh SQL và kết quả cũ, chi phí Token LLM = 0.
  - Sau mỗi quá trình Agent sinh báo cáo và được người dùng Approve qua Human-in-the-loop, kết quả sẽ tự động lưu lại vào bảng này.

### 2.3. Collection 3: `conversation_memory`
* **Mục đích**: Lưu trữ vết lịch sử công việc của các vòng lặp (Loops) trong LangGraph, thay thế cho cơ chế In-Memory quá tốn kém (nhưng kết hợp Hybrid để chống đứt gãy logic).
* **Cơ chế hoạt động**:
  - Tích hợp **Advanced Metadata Filtering**.
  - Mỗi bản ghi hội thoại/bước thực hiện đều được lưu kèm các Tag (Metadata): `task_id`, `subtask`, `step_index`, và `user_motivation`.
  - Khi Agent cần gợi nhớ, Qdrant truy xuất và Python sẽ sắp xếp theo `step_index` để khôi phục đúng trình tự thời gian. Lọc theo `task_id` & `subtask` để không lẫn lộn ngữ cảnh.

## 3. Cấu hình Kỹ thuật
- **Embedding Model**: `gemini-embedding-2`
- **Dimension Size**: 3072
- **Distance Metric**: COSINE
- **Platform**: Qdrant Cloud
