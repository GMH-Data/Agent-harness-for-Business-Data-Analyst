import os
import json
from typing import Dict, Any
from agent_core.state import AgentState
from agent_core.utils import get_gemini_client, get_safety_settings, generate_llm_content
from agent_core.qdrant_manager import retrieve_schema
from google.genai import types

def sql_node(state: AgentState) -> Dict[str, Any]:
    """
    SQL Agent (Data Extractor) - Phase 2
    """
    user_prompt = state.get("user_prompt", "")
    current_subtask = state.get("current_subtask", "")
    
    max_retries = 3
    error_feedback = ""
    
    for attempt in range(max_retries):
        try:
            client = get_gemini_client()
            prompt_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "system_prompt.md"
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            qa_feedback = state.get("qa_feedback", "")
            
            # Lấy schema từ Qdrant
            search_query = current_subtask if current_subtask else user_prompt
            rag_schema = retrieve_schema(search_query)
            
            prompt = prompt_template.replace("{user_prompt}", user_prompt).replace("{current_subtask}", current_subtask).replace("{rag_schema}", rag_schema)
            
            if qa_feedback:
                prompt += f"\n\n[QA FEEDBACK TỪ LẦN CHẠY TRƯỚC]:\n{qa_feedback}\nHãy sửa lại câu truy vấn dựa trên feedback này."
                
            if error_feedback:
                prompt += f"\n\n[LỖI TỪ LẦN THỬ TRƯỚC (Attempt {attempt})]:\n{error_feedback}\nHãy sửa lại câu truy vấn SQL để không bị lỗi này nữa."
                
            schema_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "structured_outputs.json"
            )
            with open(schema_path, "r", encoding="utf-8") as f:
                response_schema = json.load(f)
            
            config = types.GenerateContentConfig(
                temperature=0.0,
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
                step_name=f"SQL_Agent_Attempt_{attempt+1}"
            )
            
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            sql_json = json.loads(text.strip())
            generated_sql = sql_json.get("sql_query", "")
            
        except Exception as e:
            print(f"Lỗi gọi LLM SQL: {e}")
            generated_sql = "SELECT 'Error generating SQL' AS result;"
        
        from agent_core.mcp.google_mcp_client import query_bigquery
        
        print(f"Executing SQL via MCP (Attempt {attempt+1}): {generated_sql}")
        if generated_sql and not generated_sql.startswith("SELECT 'Error"):
            raw_data = query_bigquery(generated_sql)
        else:
            raw_data = "Error: No valid SQL query generated."
            
        print(f"Data retrieved: {raw_data[:200]}...") # Print first 200 chars for logging
        
        if "Database Error:" in raw_data:
            print(f"⚠️ Phát hiện lỗi SQL: {raw_data[:200]}")
            error_feedback = raw_data
            continue # Try again
        else:
            # Thành công, thoát vòng lặp
            break
    
    
    accumulated_data = state.get("accumulated_data", [])
    if not isinstance(accumulated_data, list):
        accumulated_data = []
    accumulated_data.append({"subtask": current_subtask, "raw_data": raw_data})
    
    return {
        "sql_query": generated_sql,
        "raw_data": raw_data,
        "accumulated_data": accumulated_data
    }
