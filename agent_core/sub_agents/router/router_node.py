import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from google.genai import types

def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Router Agent: Phân tích Scope và quyết định nhánh rẽ.
    """
    user_prompt = state.get("user_prompt", "")
    
    try:
        client = get_gemini_client()
        # Đọc prompt từ file
        prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            
        prompt = prompt_template.replace("{user_prompt}", user_prompt)
        
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
            step_name="Router_Agent"
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        router_json = json.loads(text.strip())
        
    except Exception as e:
        print(f"Lỗi gọi LLM: {e}")
        router_json = {
            "Scope": "Lỗi hệ thống",
            "branch": False,
            "intent": "DIRECT",
            "output": f"Xin lỗi, tôi đang gặp lỗi kết nối AI: {e}"
        }
        
    # Xác định intent: DASHBOARD / PLAN (Report) / DIRECT
    if router_json.get("branch") is True:
        intent = router_json.get("intent", "REPORT")
        # Map REPORT -> PLAN (giữ tương thích với graph.py cũ)
        current_intent = "DASHBOARD" if intent == "DASHBOARD" else "PLAN"
    else:
        current_intent = "DIRECT"
    
    return {
        "user_motivation": router_json.get("Scope", ""),
        "current_intent": current_intent,
        "draft_report": router_json.get("output", "")
    }

if __name__ == "__main__":
    test_state = {"user_prompt": "Chào bạn, AI Risser là gì vậy?"}
    print("Testing prompt 1:", test_state["user_prompt"])
    print("Result 1:", json.dumps(router_node(test_state), ensure_ascii=False, indent=2))
