from typing import Dict, Any
from agent_core.state import AgentState

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Agent: Điều phối viên.
    - Duyệt danh sách task từ plan_json dựa vào current_task_index.
    - Nếu QA reject, supervisor nhận được qa_feedback và sẽ assign lại agent để chạy lại.
    - Nếu QA approve, tăng current_task_index lên 1 để qua task tiếp theo.
    - Quyết định current_agent_assigned.
    """
    plan = state.get("plan_json", {})
    subtasks = plan.get("subtasks", [])
    current_task_index = state.get("current_task_index", 0)
    qa_status = state.get("qa_status", "")
    sub_task_proposal_str = state.get("sub_task_proposal", "")
    step_index = state.get("step_index", 0) + 1
    
    # Xử lý đề xuất Deep-Dive từ QA Subtask (sau khi qua HITL)
    hitl_response = state.get("hitl_response", "")
    
    if sub_task_proposal_str:
        if hitl_response != "reject":
            import json
            try:
                new_task = json.loads(sub_task_proposal_str)
                new_task["id"] = len(subtasks) + 1
                # Chèn subtask mới vào ngay vị trí hiện tại (vì current_task_index đã được chart_node +1)
                subtasks.insert(current_task_index, new_task)
                plan["subtasks"] = subtasks
                print(f"✅ Đã chèn Deep-Dive Subtask vào vị trí {current_task_index}: {new_task.get('description')}")
            except Exception as e:
                print(f"Lỗi parse sub_task_proposal: {e}")
        else:
            print("🚫 Người dùng đã từ chối Deep-Dive Subtask.")
            
    # Reset các biến trạng thái
    qa_status = ""
    qa_feedback = ""
    sub_task_proposal = ""
    
    # Nếu User (ở HITL cuối cùng) yêu cầu qua task tiếp theo
    if hitl_response == "subtask":
        current_task_index += 1
        
    # Xoá hitl_response sau khi đã xử lý xong
    hitl_response = ""

    # Dù là lần đầu hay là loop, Supervisor luôn gán subtask hiện tại để đưa xuống SQL Extractor
    current_task = subtasks[current_task_index] if current_task_index < len(subtasks) else {}
    desc = current_task.get("description", "")
        
    return {
        "step_index": step_index,
        "current_task_index": current_task_index,
        "plan_json": plan,
        "current_subtask": desc,
        "qa_status": qa_status,
        "qa_feedback": qa_feedback,
        "sub_task_proposal": sub_task_proposal
    }
