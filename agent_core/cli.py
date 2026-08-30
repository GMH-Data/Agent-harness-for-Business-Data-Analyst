import os
import sys

# Đảm bảo import đúng agent_core từ thư mục gốc dự án
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from agent_core.graph import app

from langfuse.decorators import observe, langfuse_context
import langfuse

@observe()
def run_chat_interaction(user_input, thread_id="cli_session_1"):
    print("\nAgent đang xử lý luồng qua LangGraph StateGraph (Phase 2)...\n")
    
    langfuse_context.update_current_trace(
        name="AI_RISSER_Chat",
        session_id=thread_id,
        tags=["cli", "langgraph", "phase_2"]
    )
    
    full_state = {"user_prompt": user_input, "task_id": thread_id}
    
    config = {
        "configurable": {"thread_id": thread_id},
        "run_name": "run_chat_interaction"
    }
    
    for chunk in app.stream(full_state, config=config, stream_mode=["updates", "debug"]):
            mode, payload = chunk
            
            if mode == "debug" and payload.get("type") == "task":
                node_name = payload.get("payload", {}).get("name", "Unknown Node")
                if node_name != "Unknown Node":
                    sys.stdout.write(f"\r\033[K\n⏳ Đang chạy: [{node_name}]\n")
                    sys.stdout.flush()
                
            elif mode == "updates":
                for node_name, node_update in payload.items():
                    print(f"\n🟢 [NODE HOÀN TẤT]: {node_name}")
                    
                    for key, val in node_update.items():
                        full_state[key] = val
                        
                        # Hiển thị trực quan output của từng node ngay khi nó chạy xong
                        if key == "plan_json":
                            subtasks = val.get('subtasks', [])
                            print(f"  => 📋 Đã lên kế hoạch: {len(subtasks)} tasks.")
                            for t in subtasks:
                                print(f"     - {t.get('description')}: {t.get('task scope')}")
                        elif key == "sql_query":
                            print(f"  => 📊 SQL Sinh ra:\n\033[96m{val}\033[0m")
                        elif key == "raw_data":
                            print(f"  => 🗃️ Dữ liệu kéo về: {len(str(val).splitlines())} dòng")
                        elif key == "chart_url":
                            print(f"  => 📈 Link Biểu Đồ:\n\033[92m{val}\033[0m")
                        elif key == "final_report" or key == "draft_report":
                            print(f"  => 📝 Nội dung:\n\033[93m{val}\033[0m")
                        elif key in ["current_intent", "user_motivation", "current_subtask"]:
                            print(f"  => ⚙️ {key.upper()}: {val}")

    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    
    print("\n" + "=" * 70)
    print("[TỔNG KẾT TOÀN BỘ TRẠNG THÁI CUỐI CÙNG]")
    if full_state.get("user_motivation"):
        print(f"  - Scope (Motivation): {full_state.get('user_motivation')}")
    if full_state.get("current_intent"):
        print(f"  - Intent: {full_state.get('current_intent')}")
    if full_state.get("plan_json"):
        print(f"  - Số Subtasks: {len(full_state.get('plan_json', {}).get('subtasks', []))}")
    if full_state.get("sql_query"):
        print(f"  - SQL Sinh Ra: \n    >>> {full_state.get('sql_query')}")
    if full_state.get("raw_data"):
        print(f"  - Kết Quả Data: \n    >>> {full_state.get('raw_data')[:300]}...")
    if full_state.get("chart_url"):
        print(f"  - Link Biểu Đồ (Chart): {full_state.get('chart_url')}")
    if full_state.get("final_report"):
        print(f"  - Insight từ Analyst: \n    >>> {full_state.get('final_report')}")
    if full_state.get("draft_report"):
        print(f"  - Trả lời trực tiếp (Direct): \n    >>> {full_state.get('draft_report')}")

    print("=" * 70)
    
def main():
    print("=" * 65)
    print("CHƯƠNG TRÌNH INTERACTIVE CLI CHAT VỚI AI RISSER (LANGGRAPH)")
    print("Nhập câu hỏi của bạn bên dưới. Nhập 'exit' hoặc 'quit' để thoát.")
    print("=" * 65)
    
    while True:
        try:
            user_input = input("\nNgười dùng: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Đã thoát chương trình chat CLI. Tạm biệt!")
                break
                
            run_chat_interaction(user_input)
                
        except KeyboardInterrupt:
            print("\nĐã ngắt chương trình.")
            break
        except Exception as e:
            print(f"\nLỗi xảy ra: {e}")

    # Ensure traces are sent before exiting
    print("Đang đồng bộ traces lên Langfuse...")
    langfuse_context.flush()

if __name__ == "__main__":
    main()
