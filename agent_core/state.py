from typing import TypedDict, Any, List

class AgentState(TypedDict):
    """
    Cấu trúc dữ liệu trung tâm của LangGraph.
    KHÔNG dùng list messages để tránh tràn token khi lặp.
    Chỉ truyền Context nhỏ nhẹ và các Metadata.
    """
    # 1. Định danh và Lịch sử
    task_id: str                # UUID quản lý toàn bộ task
    user_prompt: str            # Lời nhắc ban đầu của User
    user_motivation: str        # Mục đích sâu xa (Planner trích xuất)
    step_index: int             # Đếm số bước, dùng để sort history trên Qdrant
    
    # 2. Điều hướng và Kế hoạch
    current_intent: str         # REPORT / GWS / DASHBOARD (Router quyết định)
    plan_json: dict[str, Any]   # Cấu trúc kế hoạch các Subtask
    current_subtask: str        # Mô tả của subtask hiện tại
    current_task_index: int     # Vị trí subtask đang xử lý trong list subtasks (bắt đầu từ 0)
    current_agent_assigned: str # Tên agent được gán cho subtask hiện tại (vd: sql_extractor)
    
    # 3. Dữ liệu luân chuyển giữa các Node (Data Flow)
    sql_query: str              # Code SQL sinh ra bởi SQL Agent
    raw_data: str               # Output từ BigQuery (Tối đa 5-100 dòng hoặc schema)
    accumulated_data: list      # Danh sách data tích luỹ từ nhiều subtasks
    chart_url: str              # URL/đường dẫn biểu đồ do Chart Agent vẽ
    chart_json: str             # Dữ liệu biểu đồ dạng JSON (dùng cho Plotly UI)
    accumulated_charts: list    # Danh sách các chart tích luỹ
    draft_report: str           # Bản nháp báo cáo từ Analyst Phase 2
    
    # 4. Trạng thái QA
    qa_status: str              # approved / rejected
    qa_feedback: str            # Lời phản hồi nếu bị QA đánh reject
    sub_task_proposal: str      # Đề xuất chia nhỏ hoặc retry task từ QA

    
    # 5. Human-In-The-Loop Flag
    is_approved: bool           # User đã duyệt bản nháp chưa
    feedback: str               # Lời phản hồi nếu User Reject
    hitl_response: str          # Lựa chọn hành động tại các Node HITL (approve/reject/subtask)

    # 6. Dashboard Flow (Wireframe-First + Superset MCP)
    dashboard_blueprint: dict[str, Any]   # Blueprint JSON từ Dashboard Architect Agent
    dashboard_sections: list[dict]        # Danh sách sections đã hoàn thành (chart_config + data)
    current_section_index: int            # Section đang xử lý (0-indexed)
    current_section_goal: str             # Goal truyền tải của section hiện tại
    dashboard_preview_url: str            # URL Preview Dashboard trên Superset
    final_report: str                     # Báo cáo cuối cùng đã được duyệt

