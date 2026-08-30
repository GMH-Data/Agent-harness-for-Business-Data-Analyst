import os
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def chart_node(state: AgentState) -> Dict[str, Any]:
    """
    Chart Agent (Data Visualizer) - Phase 2
    """
    raw_data_head = state.get("raw_data", "")
    if not raw_data_head or raw_data_head == "[]" or raw_data_head.startswith("Error"):
        print("No valid data available for chart generation.")
        current_task_index = state.get("current_task_index", 0)
        return {
            "chart_json": "",
            "chart_url": "Không có dữ liệu để vẽ biểu đồ.",
            "current_task_index": current_task_index + 1
        }

    user_prompt = state.get("user_prompt", "")
    current_subtask = state.get("current_subtask", "")
    
    try:
        client = get_gemini_client()
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        qa_feedback = state.get("qa_feedback", "")
        
        prompt = prompt_template.replace("{raw_data_head}", str(raw_data_head)).replace("{user_prompt}", user_prompt).replace("{current_subtask}", current_subtask)
        
        if qa_feedback:
            prompt += f"\n\n[QA FEEDBACK TỪ LẦN CHẠY TRƯỚC]:\n{qa_feedback}\nHãy sửa lại code vẽ biểu đồ dựa trên feedback này."
        
        config = types.GenerateContentConfig(
            temperature=0.1,
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
            step_name="Chart_Agent"
        )
        
        chart_code = response.text.replace("```python", "").replace("```", "").strip()
        
        # Thực thi code Python để lấy object fig và xuất ra JSON
        import pandas as pd
        import io
        import plotly
        try:
            import json
            # raw_data_head hiện tại là chuỗi JSON do MCP trả về
            data_list = json.loads(raw_data_head)
            df = pd.DataFrame(data_list)
        except Exception as e:
            print(f"Lỗi khi parse JSON sang DataFrame: {e}")
            df = pd.DataFrame()
            
        local_env = {"df": df, "pd": pd, "plotly": plotly}
        exec(chart_code, globals(), local_env)
        
        fig = local_env.get("fig")
        if fig is not None:
            chart_json = fig.to_json()
        else:
            chart_json = ""
            
    except Exception as e:
        print(f"Lỗi gọi LLM hoặc thực thi Chart Code: {e}")
        chart_code = "print('Lỗi sinh code vẽ biểu đồ')"
        chart_json = ""
    
    chart_url = "https://storage.googleapis.com/my-bucket/chart_uuid_123.png" # Giữ nguyên cho tương thích
    
    accumulated_charts = state.get("accumulated_charts", [])
    if not isinstance(accumulated_charts, list):
        accumulated_charts = []
    if chart_json:
        accumulated_charts.append({"subtask": current_subtask, "chart_json": chart_json})
        
    current_task_index = state.get("current_task_index", 0)
        
    return {
        "chart_url": chart_url,
        "chart_json": chart_json,
        "accumulated_charts": accumulated_charts,
        "current_task_index": current_task_index + 1
    }
