import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.graph import app as graph_app
from langgraph.checkpoint.memory import MemorySaver

config = {"configurable": {"thread_id": "cli_test_hitl_1"}, "run_name": "cli_test"}

# Bước 1: Khởi tạo luồng
full_state = {"user_prompt": "Thống kê số lượng lượt truy cập trong tháng 3", "task_id": "cli_test_hitl_1"}
print("==== STARTING GRAPH ====")
for chunk in graph_app.stream(full_state, config=config, stream_mode=["updates"]):
    mode, payload = chunk
    if mode == "updates":
        if "__interrupt__" in payload:
            print("=> GRAPH INTERRUPTED!")
        else:
            print("UPDATE:", payload)

# Kiểm tra xem graph có đang dừng không
state = graph_app.get_state(config)
if state.next:
    print(f"==== GRAPH PAUSED AT {state.next[0]}. RESUMING WITH APPROVE ====")
    graph_app.update_state(config, {"hitl_response": "approve"})
    for chunk in graph_app.stream(None, config=config, stream_mode=["updates"]):
        mode, payload = chunk
        if mode == "updates":
            if "__interrupt__" in payload:
                print("=> GRAPH INTERRUPTED AGAIN!")
            else:
                print("UPDATE:", payload)

state2 = graph_app.get_state(config)
if state2.next:
    print(f"==== GRAPH PAUSED AT {state2.next[0]}. RESUMING WITH APPROVE ====")
    graph_app.update_state(config, {"hitl_response": "approve"})
    for chunk in graph_app.stream(None, config=config, stream_mode=["updates"]):
        mode, payload = chunk
        if mode == "updates":
            if "__interrupt__" in payload:
                print("=> GRAPH INTERRUPTED YET AGAIN!")
            else:
                print("UPDATE:", payload)

