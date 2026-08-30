import os
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def analyst_phase1_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyst Agent Phase 1: Phân tích 1 Subtask (Mini-analysis).
    """
    raw_data = state.get("raw_data", "")
    current_subtask = state.get("current_subtask", "")
    
    # Lấy chart gần nhất
    accumulated_charts = state.get("accumulated_charts", [])
    chart_json = ""
    if accumulated_charts:
        chart_json = accumulated_charts[-1].get("chart_json", "")
        
    try:
        client = get_gemini_client()
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt_p1.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        # Rút gọn raw_data để tiết kiệm token
        short_raw_data = str(raw_data)[:3000] + "\n...(truncated)..." if len(str(raw_data)) > 3000 else str(raw_data)
        prompt = prompt_template.replace("{raw_data}", short_raw_data).replace("{chart_json}", "(Chart data omitted to save tokens)").replace("{current_subtask}", str(current_subtask))
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            safety_settings=get_safety_settings()
        )
        
        response = generate_llm_content(
            client=client,
            model='gemma-4-31b-it',
            contents=prompt,
            config=config,
            step_name="Analyst_Agent_Phase_1"
        )
        
        mini_analysis = response.text.strip()
    except Exception as e:
        print(f"Lỗi gọi LLM Analyst P1: {e}")
        mini_analysis = f"Lỗi phân tích: {e}"
    
    # Thêm mini_analysis vào accumulated_data
    accumulated_data = state.get("accumulated_data", [])
    if not isinstance(accumulated_data, list):
        accumulated_data = []
        
    # Cập nhật object cuối cùng nếu cùng subtask
    if accumulated_data and accumulated_data[-1].get("subtask") == current_subtask:
        accumulated_data[-1]["mini_analysis"] = mini_analysis
    else:
        accumulated_data.append({
            "subtask": current_subtask,
            "raw_data": raw_data,
            "mini_analysis": mini_analysis
        })
        
    return {
        "accumulated_data": accumulated_data,
        "draft_report": mini_analysis  # Dùng tạm field này để UI render text ra block riêng
    }

def analyst_phase2_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyst Agent Phase 2: Nhận data và chart từ các agents trước,
    tổng hợp thành bản nháp (Draft Report) để đưa ra cho HITL.
    """
    accumulated_data = state.get("accumulated_data", [])
    raw_data_str = ""
    for d in accumulated_data:
        raw = str(d.get('raw_data', ''))
        short_raw = raw[:1500] + "\n...(truncated)" if len(raw) > 1500 else raw
        raw_data_str += f"\n--- Subtask: {d.get('subtask', 'Unknown')} ---\nData: {short_raw}\nPhân tích: {d.get('mini_analysis', '')}\n"
        
    chart_url = state.get("chart_url", "")
    user_prompt = state.get("user_prompt", "")
    
    plan_json = state.get("plan_json", {})
    import json
    plan_str = json.dumps(plan_json, ensure_ascii=False, indent=2)
    
    try:
        client = get_gemini_client()
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{raw_data}", raw_data_str).replace("{chart_url}", chart_url).replace("{user_prompt}", user_prompt).replace("{current_subtask}", plan_str)
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            safety_settings=get_safety_settings()
        )
        
        response = generate_llm_content(
            client=client,
            model='gemma-4-31b-it',
            contents=prompt,
            config=config,
            step_name="Analyst_Agent_Phase_2"
        )
        
        draft_report = response.text.strip()
    except Exception as e:
        print(f"Lỗi gọi LLM Analyst P2: {e}")
        draft_report = "Lỗi khi tổng hợp báo cáo nháp."
    
    return {
        "draft_report": draft_report
    }
