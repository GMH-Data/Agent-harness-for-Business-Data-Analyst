# KẾ HOẠCH TỔNG THỂ PHASE 2: AI AGENT, RAG & BI

## 1. Mục tiêu (Goal)
Chuyển đổi kho dữ liệu (Data Mart) được xây dựng ở Phase 1 thành một hệ thống hỏi đáp và phân tích thông minh. Người dùng có thể đặt câu hỏi bằng ngôn ngữ tự nhiên, hệ thống sẽ tự động viết SQL, truy vấn BigQuery, vẽ biểu đồ và phân tích Insight. 

Toàn bộ hệ thống sẽ ưu tiên triển khai trên hạ tầng **Cloud** (Qdrant Cloud, Langfuse Cloud) để tối ưu hóa tài nguyên phần cứng local.

## 2. Các thành phần chính (Core Components)

### 2.1. Hạ tầng RAG (Retrieval-Augmented Generation)
Sử dụng **Qdrant Cloud** làm Vector Database với kiến trúc 3 Bảng (Tri-Collection RAG) để tối ưu hoá chi phí Token và quản lý Context dài hạn.
- **schema_metadata**: Giúp LLM hiểu rõ cấu trúc Database (Data Dictionary).
- **validated_reports**: Semantic Cache lưu trữ báo cáo cũ.
- **conversation_memory**: Vector Memory lưu vết lịch sử với Advanced Metadata Filtering.

### 2.2. Agent Pipeline (Luồng điều phối tác vụ)
Xây dựng luồng tác tử (Agent Workflow) bằng thư viện **LangGraph**, áp dụng cơ chế đánh chặn **Human-in-the-loop (HITL)**.
- Luồng phân tích dữ liệu 4 bước (Data Science Sandwich): Analyst -> SQL -> Chart -> Analyst.
- Đảm bảo an toàn khi gọi LLM nhờ các chốt kiểm duyệt con người ở những quyết định quan trọng.

### 2.3. BI Dashboard
Sử dụng **Apache Superset** kết nối với BigQuery để xây dựng các biểu đồ tĩnh và Dashboard Cấp cao. Agent có thể cung cấp nhanh đường link các biểu đồ này cho người dùng thay vì phải vẽ lại từ đầu.

## 3. Lộ trình triển khai
- **Giai đoạn 1**: Thiết lập hạ tầng Cloud RAG và Langfuse Observability (Hoàn thành).
- **Giai đoạn 2**: Xây dựng cấu trúc Tri-Collection RAG và nạp Schema (Hoàn thành).
- **Giai đoạn 3**: Lập trình luồng LangGraph Agent Pipeline với HITL (Đang triển khai).
- **Giai đoạn 4**: Tích hợp các công cụ MCP (BigQuery, Superset, Python Sandbox) cho Agent (Sắp tới).
- **Giai đoạn 5**: Viết Test và Đánh giá (Evaluation).
