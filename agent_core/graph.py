from langgraph.graph import StateGraph, END
from agent_core.state import AgentState

# Import các Nodes
from agent_core.sub_agents.router.router_node import router_node
from agent_core.sub_agents.planner.planner_node import planner_node
from agent_core.sub_agents.supervisor.supervisor_node import supervisor_node
from agent_core.sub_agents.analyst.analyst_node import analyst_phase1_node, analyst_phase2_node
from agent_core.sub_agents.sql_expert.sql_node import sql_node
from agent_core.sub_agents.chart_visualizer.chart_node import chart_node
from agent_core.sub_agents.qa_agent.qa_node import qa_node
from agent_core.sub_agents.qa_agent.qa_subtask_node import qa_subtask_node

# Import Dashboard Nodes
from agent_core.sub_agents.dashboard_architect.architect_node import architect_node
from agent_core.sub_agents.dashboard_filler.filler_node import filler_node
from agent_core.sub_agents.dashboard_assembler.assembler_node import assembler_node

def plan_hitl_node(state: AgentState):
    """Node duyệt Plan (Report flow)"""
    return {}

def report_hitl_node(state: AgentState):
    """Node duyệt Report hoàn chỉnh"""
    draft = state.get("draft_report", "")
    return {"final_report": draft}

def blueprint_hitl_node(state: AgentState):
    """Node duyệt Dashboard Blueprint"""
    return {}

def dashboard_hitl_node(state: AgentState):
    """Node duyệt Dashboard hoàn chỉnh"""
    return {}

def section_setup_node(state: AgentState):
    """Setup context cho SQL Agent truy vấn data của từng section"""
    blueprint = state.get("dashboard_blueprint", {})
    sections = blueprint.get("sections", [])
    current_index = state.get("current_section_index", 0)
    
    # Delay 10s giữa mỗi section để tránh quota exhaustion
    if current_index > 0:
        import time
        print(f"⏱ Đợi 10 giây trước khi xử lý section {current_index + 1}/{len(sections)}...")
        time.sleep(10)
    
    if current_index < len(sections):
        section = sections[current_index]
        return {
            "current_subtask": f"Lấy dữ liệu cho section: {section.get('section_id')}. Mục tiêu: {section.get('goal')}. Yêu cầu dữ liệu: {section.get('data_scope')}",
            "current_section_goal": section.get("goal", "")
        }
    return {}

def done_node(state: AgentState):
    return {}

def cleanup_node(state: AgentState):
    task_id = state.get("task_id", "")
    print(f"[{task_id}] Đang dọn dẹp bộ nhớ trung gian Qdrant...")
    return {"step_index": -1} 

def qa_hitl_node(state: AgentState):
    return {}


# ==== Định tuyến ====
def route_from_router(state: AgentState):
    intent = state.get("current_intent", "")
    if intent == "PLAN":
        return "planner"
    elif intent == "DASHBOARD":
        return "architect"
    return "cleanup"

def route_from_supervisor(state: AgentState):
    plan = state.get("plan_json", {})
    subtasks = plan.get("subtasks", [])
    current_task_index = state.get("current_task_index", 0)
    
    if current_task_index < len(subtasks):
        return "sql_extractor"
    return "analyst_p2"

def route_from_plan_hitl(state: AgentState):
    response = state.get("hitl_response", "approve")
    if response == "reject":
        return "planner"
    return "supervisor"

def route_from_sql(state: AgentState):
    intent = state.get("current_intent", "")
    if intent == "DASHBOARD":
        return "dashboard_filler"
    return "chart_visualizer"

def route_from_qa(state: AgentState):
    qa_status = state.get("qa_status", "approved")
    if qa_status == "rejected":
        return "qa_hitl"
    return "report_hitl"

def route_from_qa_hitl(state: AgentState):
    # Always return to supervisor. Supervisor will check hitl_response to see if it should append the subtask.
    return "supervisor"

def route_from_qa_subtask(state: AgentState):
    proposal = state.get("sub_task_proposal", "")
    if proposal:
        return "qa_hitl"
    return "supervisor"

def route_from_report_hitl(state: AgentState):
    response = state.get("hitl_response", "approve")
    if response == "subtask":
        return "supervisor"
    return "cleanup"

def route_from_blueprint_hitl(state: AgentState):
    response = state.get("hitl_response", "approve")
    if response == "reject":
        return "architect"
    blueprint = state.get("dashboard_blueprint", {})
    sections = blueprint.get("sections", [])
    if len(sections) == 0:
        return "dashboard_assembler"
    return "section_setup"

def route_from_filler(state: AgentState):
    blueprint = state.get("dashboard_blueprint", {})
    sections = blueprint.get("sections", [])
    current_index = state.get("current_section_index", 0)
    
    # Nếu vẫn còn section chưa làm
    if current_index < len(sections):
        return "section_setup"
    # Đã xong tất cả section
    return "dashboard_assembler"


# ==== Khởi tạo Graph ====
workflow = StateGraph(AgentState)

# Report Flow Nodes
workflow.add_node("router", router_node)
workflow.add_node("planner", planner_node)
workflow.add_node("plan_hitl", plan_hitl_node)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("qa_subtask", qa_subtask_node)
workflow.add_node("qa_agent", qa_node)
workflow.add_node("qa_hitl", qa_hitl_node)
workflow.add_node("analyst_p1", analyst_phase1_node)
workflow.add_node("sql_extractor", sql_node)
workflow.add_node("chart_visualizer", chart_node)
workflow.add_node("analyst_p2", analyst_phase2_node)
workflow.add_node("report_hitl", report_hitl_node)

# Dashboard Flow Nodes
workflow.add_node("architect", architect_node)
workflow.add_node("blueprint_hitl", blueprint_hitl_node)
workflow.add_node("section_setup", section_setup_node)
workflow.add_node("dashboard_filler", filler_node)
workflow.add_node("dashboard_assembler", assembler_node)
workflow.add_node("dashboard_hitl", dashboard_hitl_node)

# Common Nodes
workflow.add_node("done", done_node)
workflow.add_node("cleanup", cleanup_node)


# ==== Cấu hình Edges ====
workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_from_router)
workflow.add_conditional_edges("sql_extractor", route_from_sql)

# --- REPORT BRANCH ---
workflow.add_edge("planner", "plan_hitl")
workflow.add_conditional_edges("plan_hitl", route_from_plan_hitl)
workflow.add_conditional_edges("supervisor", route_from_supervisor)
workflow.add_edge("chart_visualizer", "analyst_p1")
workflow.add_edge("analyst_p1", "qa_subtask")
workflow.add_conditional_edges("qa_subtask", route_from_qa_subtask)
workflow.add_edge("analyst_p2", "qa_agent")
workflow.add_conditional_edges("qa_agent", route_from_qa)
workflow.add_conditional_edges("qa_hitl", route_from_qa_hitl)
workflow.add_conditional_edges("report_hitl", route_from_report_hitl)


# --- DASHBOARD BRANCH ---
workflow.add_edge("architect", "blueprint_hitl")
workflow.add_conditional_edges("blueprint_hitl", route_from_blueprint_hitl)
workflow.add_edge("section_setup", "sql_extractor") # Re-use SQL Extractor
workflow.add_conditional_edges("dashboard_filler", route_from_filler)
workflow.add_edge("dashboard_assembler", "dashboard_hitl")
workflow.add_edge("dashboard_hitl", "cleanup") # Done, go to cleanup

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

# Biên dịch Graph
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["plan_hitl", "report_hitl", "qa_hitl", "blueprint_hitl", "dashboard_hitl"]
)
