# KẾ HOẠCH TRIỂN KHAI MÃ NGUỒN CÁC AGENT (TỐI ƯU TOKEN)

## [Goal Description]
Thiết lập kiến trúc mã nguồn cho các Agent trong hệ thống LangGraph, tập trung tối đa vào việc **giảm tải Token In-memory** (tránh tình trạng phình to Token khi lặp nhiều bước) và **phân chia trách nhiệm rõ ràng** (Single Responsibility Principle) để mỗi Agent chỉ nhận đúng lượng dữ liệu (Context) mà nó cần.

## 1. Cấu trúc State của LangGraph (State.py)
Truyền thống, LangGraph sử dụng mảng `messages: Annotated[list[AnyMessage], add_messages]` để lưu toàn bộ hội thoại. Trong dự án này, chúng ta sẽ **KHÔNG** truyền chuỗi tin nhắn dài.
Thay vào đó, State sẽ chỉ lưu siêu dữ liệu và trạng thái hiện tại:
```python
class AgentState(TypedDict):
    task_id: str
    user_motivation: str
    current_intent: str      # Kết quả từ Router (GWS / REPORT / DASH)
    plan_json: dict          # Kế hoạch chi tiết từ Planner
    current_subtask: str     # Đang chạy nhánh nào
    step_index: int          # Đếm số bước để giới hạn loop
    raw_data: str            # Output từ BigQuery (Giới hạn 100 dòng đầu để tiết kiệm token)
    chart_url: str           # Output từ Chart Agent
    draft_report: str        # Bản nháp báo cáo
```

## 2. Chiến lược Tối ưu Token cho từng Agent

### 2.1. Router Agent (Siêu nhẹ)
- **Nhiệm vụ**: Phân loại ý định của người dùng.
- **Tối ưu Token**: 
  - Chỉ nhận Prompt gốc của User. KHÔNG đọc `conversation_memory`.
  - Output bắt buộc phải là 1 từ khoá duy nhất: `REPORT`, `GWS`, `DASHBOARD`, hoặc `GREETING`.

### 2.2. Planner Agent
- **Nhiệm vụ**: Bẻ gãy câu hỏi phức tạp thành Kế hoạch JSON.
- **Tối ưu Token**:
  - Đọc 3 bước hội thoại gần nhất (nhờ `recall_memory`).
  - Sử dụng prompt ép kiểu trả về JSON chuẩn (Structued Output) để tránh LLM giải thích dông dài.

### 2.3. SQL Agent (Data Extractor)
- **Nhiệm vụ**: Dịch Text-to-SQL và gọi BigQuery.
- **Tối ưu Token cực hạn bằng Schema RAG**:
  - Thay vì bơm toàn bộ sơ đồ 50 bảng BigQuery vào System Prompt, SQL Agent sẽ chạy `get_qdrant_client().search(...)` với câu hỏi của người dùng để lấy ra đúng **2 bảng liên quan nhất** từ `schema_metadata`.
  - System Prompt của SQL Agent chỉ chứa JSON Schema của 2 bảng đó. Tiết kiệm 95% token so với cách nhồi DDL toàn bộ DB.
  - Áp dụng Tool Call để trả về SQL.

### 2.4. Chart Agent (Data Visualizer)
- **Nhiệm vụ**: Viết code Python vẽ biểu đồ.
- **Tối ưu Token (Data Chunking)**:
  - Nếu kết quả BigQuery trả về 10,000 dòng, việc nhồi tất cả vào Prompt cho Chart Agent sẽ gây lãng phí khủng khiếp và dễ crash.
  - **Giải pháp**: Chỉ truyền cấu trúc Cột (Columns) và **5 dòng dữ liệu mẫu (head 5)** vào cho Chart Agent. LLM chỉ cần hiểu format dữ liệu để viết code Python, còn code Python chạy cục bộ sẽ load toàn bộ DataFrame thực tế.

### 2.5. Analyst Agent (Phase 1 & Phase 2)
- **Nhiệm vụ Phase 1**: Đọc yêu cầu -> Phân tích Metrics cần lấy.
  - **Tối ưu**: Tra Semantic Cache (`validated_reports`). Nếu Hit Cache -> Trả kết quả cũ ngay lập tức, bỏ qua toàn bộ SQL và Chart Agent. (Tiết kiệm 100% token luồng dưới).
- **Nhiệm vụ Phase 2**: Đọc biểu đồ + Raw Data -> Viết Insight.
  - **Tối ưu**: Chỉ đưa vào Tóm tắt thống kê (Pandas `df.describe()`) thay vì toàn bộ Raw Data.
