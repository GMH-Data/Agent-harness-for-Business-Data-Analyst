import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.sub_agents.sql_expert.sql_node import sql_node

state = {"user_prompt": "tháng 3 có bao nhiêu lượt truy cập"}
print(sql_node(state))
