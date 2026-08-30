import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Agent: Lập kế hoạch chi tiết với 4 cột theo yêu cầu.
    """
    user_prompt = state.get("user_prompt", "")
    global_goal = state.get("user_motivation", "Mục tiêu tổng quát")
    
    try:
        client = get_gemini_client()
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{user_prompt}", user_prompt).replace("{global_goal}", global_goal)
        
        # Đường dẫn tới schema json
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
            step_name="Planner_Agent"
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        plan_json = json.loads(text.strip())
        
    except Exception as e:
        print(f"Lỗi gọi LLM Planner: {e}")
        plan_json = {"subtasks": []}
        
    return {
        "plan_json": plan_json
    }

if __name__ == "__main__":
    test_state = {
        "user_prompt": "Lấy tổng doanh thu quý 3 vẽ biểu đồ tròn và báo cáo insight cho tôi",
        "user_motivation": "Báo cáo doanh thu quý 3"
    }
    print("Testing Planner:", test_state["user_prompt"])
    print("Result:", json.dumps(planner_node(test_state), ensure_ascii=False, indent=2))
