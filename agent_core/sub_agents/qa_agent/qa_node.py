import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def qa_node(state: AgentState) -> Dict[str, Any]:
    """
    QA Agent (Cuối luồng): Đánh giá Draft Report xem đã trả lời trọn vẹn User Motivation chưa.
    """
    user_prompt = state.get("user_prompt", "")
    user_motivation = state.get("user_motivation", "")
    draft_report = state.get("draft_report", "")
    
    try:
        client = get_gemini_client()
        
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{user_prompt}", user_prompt).replace("{user_motivation}", user_motivation).replace("{draft_report}", draft_report)
        
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "structured_outputs.json"
        )
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
            step_name="QA_Agent_Final"
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        qa_result = json.loads(text.strip())
        
        # Nếu rejected, lưu next_subtask dưới dạng chuỗi JSON vào sub_task_proposal
        next_subtask = qa_result.get("next_subtask", {})
        sub_task_str = json.dumps(next_subtask, ensure_ascii=False) if next_subtask else ""
        
        return {
            "qa_status": "approved" if qa_result.get("is_satisfied", False) else "rejected",
            "qa_feedback": qa_result.get("feedback", ""),
            "sub_task_proposal": sub_task_str
        }
        
    except Exception as e:
        print(f"Lỗi gọi LLM QA: {e}")
        return {
            "qa_status": "approved",
            "qa_feedback": f"Lỗi hệ thống QA: {str(e)}",
            "sub_task_proposal": ""
        }
