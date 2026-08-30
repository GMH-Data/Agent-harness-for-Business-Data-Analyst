import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types


def filler_node(state: AgentState) -> Dict[str, Any]:
    """
    Dashboard Filler Agent:
    1. Nhận raw_data từ SQL Agent + current_section_goal từ Blueprint
    2. Sinh Superset Chart Configuration JSON
    3. Append kết quả vào dashboard_sections[]
    4. Tăng current_section_index
    """
    raw_data = state.get("raw_data", "")
    current_section_goal = state.get("current_section_goal", "")
    user_prompt = state.get("user_prompt", "")
    blueprint = state.get("dashboard_blueprint", {})
    current_index = state.get("current_section_index", 0)
    sections_done = state.get("dashboard_sections", []) or []
    
    # Lấy thông tin section hiện tại từ blueprint
    all_sections = blueprint.get("sections", [])
    current_section = all_sections[current_index] if current_index < len(all_sections) else {}
    
    if not raw_data or raw_data.startswith("Error"):
        # Nếu không có data, tạo placeholder
        chart_config = {
            "chart_type": "table",
            "chart_name": f"No Data - {current_section.get('section_id', 'unknown')}",
            "metrics": [],
            "groupby": [],
            "note": "Không có dữ liệu cho section này"
        }
    else:
        try:
            client = get_gemini_client()
            
            prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.md")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            
            prompt = prompt_template.replace("{raw_data_head}", str(raw_data)[:2000])\
                                    .replace("{user_prompt}", user_prompt)\
                                    .replace("{section_goal}", current_section_goal)\
                                    .replace("{suggested_chart_type}", current_section.get("suggested_chart_type", ""))\
                                    .replace("{section_id}", current_section.get("section_id", ""))
            
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "structured_outputs.json")
            with open(schema_path, "r", encoding="utf-8") as f:
                response_schema = json.load(f)
            
            config = types.GenerateContentConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=response_schema,
                safety_settings=get_safety_settings()
            )
            
            response = generate_llm_content(
                client=client,
                model='gemma-4-31b-it',
                contents=prompt,
                config=config,
                step_name=f"Dashboard_Filler_Section_{current_index}"
            )
            
            text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            chart_config = json.loads(text)
            
        except Exception as e:
            print(f"Lỗi gọi LLM Dashboard Filler: {e}")
            chart_config = {
                "chart_type": current_section.get("suggested_chart_type", "table"),
                "chart_name": f"Error - {current_section.get('section_id', '')}",
                "metrics": [],
                "error": str(e)
            }
    
    # Append section hoàn thành
    completed_section = {
        "section_id": current_section.get("section_id", f"section_{current_index}"),
        "section_goal": current_section_goal,
        "chart_config": chart_config,
        "raw_data": raw_data,
        "sql_query": state.get("sql_query", "")
    }
    sections_done.append(completed_section)
    
    return {
        "dashboard_sections": sections_done,
        "current_section_index": current_index + 1
    }
