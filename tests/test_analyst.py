import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.sub_agents.analyst.analyst_node import analyst_phase2_node
import time

state = {
    "raw_data": "month,total\n2023-07,15000\n2023-08,22000\n2023-09,18000",
    "chart_url": "https://storage.googleapis.com/my-bucket/chart_uuid_123.png",
    "user_prompt": "tháng 3 có bao nhiêu lượt truy cập"
}
t0 = time.time()
print("Calling analyst_phase2_node...")
result = analyst_phase2_node(state)
print("Finished in", time.time() - t0, "seconds")
print(result)
