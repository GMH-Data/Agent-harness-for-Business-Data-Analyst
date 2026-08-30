import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def qa_subtask_node(state: AgentState) -> Dict[str, Any]:
    """
    QA Subtask Agent: Kiểm tra mini-report của Analyst P1.
    Phát hiện bất thường và đề xuất Deep-Dive subtask nếu cần.
    """
    accumulated_data = state.get("accumulated_data", [])
    if not accumulated_data:
        return {}
        
    last_data = accumulated_data[-1]
    mini_analysis = last_data.get("mini_analysis", "")
    current_subtask = state.get("current_subtask", "")
    user_motivation = state.get("user_motivation", "")
    
    try:
        client = get_gemini_client()
        
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt_subtask.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{user_motivation}", user_motivation).replace("{current_subtask}", str(current_subtask)).replace("{mini_analysis}", mini_analysis)
        
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "structured_outputs_subtask.json"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            response_schema = json.load(f)
            
        config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            response_mime_type="application/json",
            response_schema=response_schema,
            safety_settings=get_safety_settings()
        )
        
        response = generate_llm_content(
            client=client,
            model='gemma-4-31b-it',
            contents=prompt,
            config=config,
            step_name="QA_Agent_Subtask"
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        qa_result = json.loads(text.strip())
        
        needs_deepdive = qa_result.get("needs_deepdive", False)
        sub_task_proposal = ""
        if needs_deepdive and qa_result.get("next_subtask"):
            sub_task_proposal = json.dumps(qa_result.get("next_subtask"), ensure_ascii=False)
            
        return {
            "sub_task_proposal": sub_task_proposal
        }
        
    except Exception as e:
        print(f"Lỗi gọi LLM QA Subtask: {e}")
        return {
            "sub_task_proposal": ""
        }
