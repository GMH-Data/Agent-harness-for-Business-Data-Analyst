import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.graph import app as graph_app
from langgraph.checkpoint.memory import MemorySaver

config = {"configurable": {"thread_id": "cli_test_hitl_file_1"}, "run_name": "cli_test"}
output_file = "test_output.txt"

with open(output_file, "w", encoding="utf-8") as f:
    # Bước 1: Khởi tạo luồng
    full_state = {"user_prompt": "Thống kê số lượng lượt truy cập trong tháng 3", "task_id": "cli_test_hitl_file_1"}
    f.write("==== STARTING GRAPH ====\n")
    for chunk in graph_app.stream(full_state, config=config, stream_mode=["updates"]):
        mode, payload = chunk
        if mode == "updates":
            if "__interrupt__" in payload:
                f.write("=> GRAPH INTERRUPTED!\n")
            else:
                f.write(f"UPDATE: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

    # Kiểm tra xem graph có đang dừng không
    state = graph_app.get_state(config)
    if state.next:
        f.write(f"==== GRAPH PAUSED AT {state.next[0]}. RESUMING WITH APPROVE ====\n")
        graph_app.update_state(config, {"hitl_response": "approve"})
        for chunk in graph_app.stream(None, config=config, stream_mode=["updates"]):
            mode, payload = chunk
            if mode == "updates":
                if "__interrupt__" in payload:
                    f.write("=> GRAPH INTERRUPTED AGAIN!\n")
                else:
                    f.write(f"UPDATE: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

    state2 = graph_app.get_state(config)
    if state2.next:
        f.write(f"==== GRAPH PAUSED AT {state2.next[0]}. RESUMING WITH APPROVE ====\n")
        graph_app.update_state(config, {"hitl_response": "approve"})
        for chunk in graph_app.stream(None, config=config, stream_mode=["updates"]):
            mode, payload = chunk
            if mode == "updates":
                if "__interrupt__" in payload:
                    f.write("=> GRAPH INTERRUPTED YET AGAIN!\n")
                else:
                    f.write(f"UPDATE: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

print(f"Hoàn thành việc test. Kết quả đã lưu vào {output_file}")
