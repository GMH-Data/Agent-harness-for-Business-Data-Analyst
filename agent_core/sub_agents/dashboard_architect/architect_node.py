import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from agent_core.qdrant_manager import retrieve_schema
from agent_core.memory_manager import check_semantic_cache
from google.genai import types


def architect_node(state: AgentState) -> Dict[str, Any]:
    """
    Dashboard Architect Agent:
    1. Nhận user_prompt + user_motivation
    2. Truy vấn RAG (validated_reports) để tìm Template Layout tương tự
    3. Truy vấn RAG (schema_metadata) để hiểu cấu trúc dữ liệu
    4. Sinh Blueprint JSON gồm: dashboard_name, storyline, sections[]
    5. Trả về state: dashboard_blueprint, dashboard_sections (rỗng ban đầu)
    """
    user_prompt = state.get("user_prompt", "")
    user_motivation = state.get("user_motivation", "")
    
    try:
        client = get_gemini_client()
        
        # Load system prompt
        prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        # RAG: Truy xuất Schema để hiểu cấu trúc dữ liệu
        rag_schema = retrieve_schema(user_prompt)
        
        # RAG: Tìm Template Layout tương tự từ cache
        cached = check_semantic_cache(user_prompt)
        template_context = ""
        if cached:
            template_context = f"Đã tìm thấy Dashboard Template tương tự từ lịch sử:\n{cached.get('report_data', '')}"
        
        prompt = prompt_template.replace("{user_prompt}", user_prompt)\
                                .replace("{user_motivation}", user_motivation)\
                                .replace("{rag_schema}", rag_schema)\
                                .replace("{template_context}", template_context)
        
        # Load structured output schema
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
            step_name="Dashboard_Architect_Agent"
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        try:
            blueprint = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Lỗi parse JSON: {e}")
            print(f"Raw text: {text}")
            raise e
        
    except Exception as e:
        print(f"Lỗi gọi LLM Dashboard Architect: {e}")
        blueprint = {
            "dashboard_name": "Error Dashboard",
            "storyline": f"Lỗi khi thiết kế: {e}",
            "sections": []
        }
    
    return {
        "dashboard_blueprint": blueprint,
        "dashboard_sections": [],      # Khởi tạo rỗng, sẽ được fill bởi Filler Agent
        "current_section_index": 0,
        "draft_report": f"📐 **Blueprint Dashboard: {blueprint.get('dashboard_name', '')}**\n\n"
                        f"🎯 Storyline: {blueprint.get('storyline', '')}\n\n"
                        f"📊 Số sections: {len(blueprint.get('sections', []))}\n\n"
                        + "\n".join([
                            f"  - **{s.get('section_id', '')}** (Row {s.get('row', '')}, Span {s.get('col_span', '')}): "
                            f"{s.get('goal', '')} → {s.get('suggested_chart_type', '')}"
                            for s in blueprint.get('sections', [])
                        ])
    }
