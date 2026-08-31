# Mô Tả Bản Vẽ: Agent RAG Ingestion & Retrieval Flow

Bản vẽ [rag_vector_flow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/rag_vector_flow.drawio.png) mô tả chi tiết luồng xử lý RAG (Retrieval-Augmented Generation) của AI RISSER, chia làm 2 giai đoạn: Giai đoạn nạp dữ liệu (Ingestion Pipeline) và Giai đoạn truy xuất ngữ cảnh phục vụ thực thi của Agent (Retrieval & Execution Flow).

## 1. Phân luồng 1: Ingestion & Chunking Pipeline (Thiết lập Bộ nhớ)
Quy trình này tự động hóa việc đưa tri thức về cấu trúc cơ sở dữ liệu (Database Schema) vào bộ nhớ Vector:

1.  **Đầu vào (`dbt schema.yml`):** Chứa các khai báo cấu trúc bảng thuộc Gold layer đã được dbt và các kỹ sư định nghĩa.
2.  **YAML Parser & Schema Extractor:** Bộ đọc phân tích cấu trúc file YAML để lọc ra danh sách các bảng và thông tin cột tương ứng.
3.  **Table-Level Chunking:** Cơ chế chia nhỏ tri thức theo cấp độ bảng. Mỗi bảng dữ liệu được gom thành 1 chunk gồm:
    *   *Search text (Dùng để tìm kiếm):* Chuỗi tóm tắt `"Bảng [tên bảng]: [mô tả chức năng]"`.
    *   *Payload (Dữ liệu đính kèm):* Chuỗi JSON chứa toàn bộ định nghĩa các cột (`name`, `description`, `type`).
4.  **Gemini Embedding API (`gemini-embedding-2`):** Nhúng (Vectorize) phần `search_text` thành vector 3072 chiều.
5.  **Lưu trữ (Qdrant `schema_metadata`):** Ghi đè/cập nhật điểm vector kèm Payload tương ứng vào Collection.

## 2. Phân luồng 2: Retrieval & Agent Execution Flow (Truy xuất)
Khi người dùng tương tác, luồng truy xuất tự động diễn ra:

1.  **User Query:** Người dùng nhập yêu cầu bằng ngôn ngữ tự nhiên.
2.  **Vectorize Prompt:** Gọi Gemini Embedding API biến đổi câu hỏi thành vector.
3.  **Semantic Cache Check (`validated_reports`):** Hệ thống kiểm tra nhanh xem câu hỏi này từng được phân tích thành công trước đây chưa. Nếu có (cache hit), trả về kết quả ngay lập tức để tiết kiệm chi phí.
4.  **Qdrant Vector Search:** Nếu cache miss, hệ thống dùng vector câu hỏi để tìm kiếm các bảng dữ liệu tương đồng nhất trên collection `schema_metadata`.
5.  **Inject context to SQL Expert Agent:** Trả về cấu trúc cột chi tiết (Payload JSON) của **Top 3 bảng phù hợp nhất**, bơm trực tiếp vào prompt ngữ cảnh của SQL Agent.
6.  **Execute Query:** SQL Agent viết câu lệnh SQL hoàn hảo và gửi cho **Google BigQuery** thực thi, hoàn toàn tránh được lỗi ảo giác về cấu trúc bảng/cột.

---
*Xem sơ đồ trực quan tại: [rag_vector_flow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/rag_vector_flow.drawio.png)*
