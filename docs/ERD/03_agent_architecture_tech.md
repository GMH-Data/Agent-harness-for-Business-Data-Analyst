# Mô Tả Bản Vẽ: Agent Architecture & Tech Stack

Bản vẽ [agent_architecture_tech.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/agent_architecture_tech.drawio.png) mô tả sơ đồ kiến trúc hệ thống và ngăn xếp công nghệ (Tech Stack) của AI Agent Core trong hệ sinh thái AI RISSER.

## 1. Các thành phần và mối tương tác công nghệ
Sơ đồ bao gồm các khối chức năng tương tác hai chiều chặt chẽ:

1.  **Giao diện Người dùng (User Interface Layer):**
    *   **React App (Vite):** Frontend xây dựng với giao diện thẩm mỹ cao (Tailwind CSS, Glassmorphism). Giao tiếp với backend thông qua cơ chế **Server-Sent Events (SSE)** để hiển thị luồng suy nghĩ của AI theo thời gian thực (Streaming thoughts).
2.  **Bộ điều phối Agentic (Agent Core Layer):**
    *   **FastAPI Backend:** Đóng vai trò là REST API Server quản lý phiên chạy, định tuyến các yêu cầu. Được deploy container hóa trên **Google Cloud Run** với cơ chế Auto-scaling.
    *   **LangGraph Orchestration:** Trái tim điều phối luồng logic của các Agent chuyên biệt bằng cách quản lý cỗ máy trạng thái (State Machine) kèm cơ chế dừng chờ duyệt của con người (**Human-in-the-Loop**).
    *   **Gemini 1.5 Pro & Flash (Google GenAI SDK):** Đóng vai trò làm bộ não suy luận.
3.  **Tầng lưu trữ & Tìm kiếm ngữ cảnh (Database & Retrieval Layer):**
    *   **Qdrant Vector DB:** Quản lý 3 collection:
        *   `schema_metadata`: Lưu trữ DDL JSON cấu trúc bảng BigQuery để phục vụ Schema RAG.
        *   `validated_reports`: Lưu trữ các mẫu Dashboard và câu lệnh SQL từng được duyệt để làm Semantic Cache.
        *   `conversation_memory`: Lưu bộ nhớ hội thoại ngữ cảnh dài hạn của người dùng.
    *   **Google BigQuery:** Kho dữ liệu Gold Layer nơi chứa các dữ liệu sạch để SQL Agent thực thi các câu lệnh SELECT kiểm nghiệm dữ liệu.
4.  **Tầng trực quan hoá & Tích hợp (BI & Integration Layer):**
    *   **Apache Superset:** Nhận cấu hình Chart JSON sinh ra từ Dashboard Agent qua giao thức **Model Context Protocol (FastMCP)** để tự động lắp ráp thành biểu đồ và Dashboard bản nháp (Draft Preview) gửi lại link cho người dùng.

---
*Xem sơ đồ trực quan tại: [agent_architecture_tech.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/agent_architecture_tech.drawio.png)*
