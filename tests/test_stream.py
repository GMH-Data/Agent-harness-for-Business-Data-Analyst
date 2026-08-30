import sys
import os
import json
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.graph import app as graph_app

thread_id = f"cli_test_{uuid.uuid4().hex[:8]}"
config = {"configurable": {"thread_id": thread_id}, "run_name": "cli_test"}
state = {"user_prompt": "tháng 3 có bao nhiêu lượt truy cập"}

print(f"==== BẮT ĐẦU GRAPH (Thread: {thread_id}) ====")
for update in graph_app.stream(state, config, stream_mode="updates"):
    if "__interrupt__" in update:
        print("=> ĐÃ TẠM DỪNG TẠI PLAN HITL!")
        break
    print("UPDATE:", update)

print("==== TỰ ĐỘNG DUYỆT (APPROVE) TẠI PLAN_HITL ====")
for update in graph_app.stream(None, config, stream_mode="updates"):
    if "__interrupt__" in update:
        print("=> ĐÃ TẠM DỪNG TẠI REPORT HITL!")
        break
    print("UPDATE:", update)

print("==== TỰ ĐỘNG DUYỆT (APPROVE) TẠI REPORT_HITL ====")
for update in graph_app.stream(None, config, stream_mode="updates"):
    print("UPDATE:", update)
