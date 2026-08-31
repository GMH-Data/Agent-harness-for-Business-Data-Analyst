# Mô Tả Bản Vẽ: LangGraph Agent Workflow

Bản vẽ [agent_workflow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/agent_workflow.drawio.png) mô tả chi tiết cỗ máy trạng thái (State Machine) điều phối luồng làm việc của các Agent bên trong hệ thống AI RISSER sử dụng khung điều phối LangGraph.

## 1. Các Node (Agent) chính trong luồng
Luồng xử lý bao gồm các chặng quyết định logic:

1.  **Ý định người dùng (User Prompt):** Bắt đầu khi người dùng gửi yêu cầu thông qua API.
2.  **Intent Router:** Định tuyến yêu cầu thành 3 hướng chính:
    *   `DIRECT`: Trả lời trực tiếp bằng văn bản nếu đó là câu giao tiếp thông thường.
    *   `REPORT`: Thực hiện phân tích dữ liệu ad-hoc (luồng 1).
    *   `DASHBOARD`: Thiết kế và lắp ráp Dashboard đa biểu đồ trên Superset (luồng 2).
3.  **Master Planner (Luồng 1 & 2):** Phân rã mục tiêu lớn của người dùng thành một danh sách các công việc con (JSON subtasks list) có tuần tự.
4.  **Supervisor Loop (Vòng lặp điều hành):** Chạy tuần tự qua từng Subtask. Đối với mỗi subtask, Supervisor sẽ gọi các Agent nhánh thực thi:
    *   **SQL Expert Agent:** Thực hiện viết câu lệnh SQL để lấy dữ liệu.
    *   **QA Agent (Vòng lặp tự sửa đổi - ReAct loop):** Kiểm định câu lệnh SQL và kết quả dữ liệu trả về từ BigQuery. Nếu phát hiện lỗi hoặc bất thường dữ liệu, QA sẽ trả lại feedback ép SQL Agent phải tự viết lại.
    *   **Chart Visualizer Agent:** Nhận dữ liệu sạch để sinh ra cấu hình Plotly vẽ biểu đồ.
5.  **Luồng Dashboard (Luồng 2):**
    *   **Dashboard Architect:** Thiết kế cấu trúc hàng/cột (Blueprint) cho Dashboard.
    *   **Dashboard Filler:** Nhận dữ liệu thô từ SQL Agent để sinh cấu hình biểu đồ của Superset.
    *   **Dashboard Assembler:** Tổng hợp toàn bộ các biểu đồ con để gọi Superset FastMCP ráp thành Dashboard nháp hoàn chỉnh.
6.  **Human-in-the-Loop (HITL) Gate:** Chốt chặn tạm dừng luồng chạy (Interrupt). AI gửi kết quả nháp lên giao diện và chờ người dùng bấm "Approve" (Duyệt) mới chính thức phát hành kết quả.

---
*Xem sơ đồ trực quan tại: [agent_workflow.drawio.png](file:///home/gmh/Project/AI%20RISSER/docs/ERD/Final/agent_workflow.drawio.png)*
