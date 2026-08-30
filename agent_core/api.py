import os
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agent_core.graph import app as agent_graph

app = FastAPI(title="AI RISSER Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
import json
from fastapi.responses import StreamingResponse
from langgraph.types import Command
from langgraph.errors import GraphInterrupt

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        config = {"configurable": {"thread_id": req.thread_id}}
        message = req.message.strip().lower()
        
        try:
            # Check if this is a HITL action
            if message in ["approve", "reject", "subtask"]:
                yield f"data: {json.dumps({'type': 'status', 'content': f'Đã nhận lệnh HITL: {message.upper()}'})}\n\n"
                
                # Use Command to resume the graph
                async for event in agent_graph.astream(Command(resume=message), config=config):
                    node_name = list(event.keys())[0]
                    node_data = event[node_name]
                    
                    yield f"data: {json.dumps({'type': 'node_finish', 'node': node_name, 'data': node_data})}\n\n"
                    await asyncio.sleep(random.uniform(1.0, 3.0))
            else:
                # Normal start with new prompt
                yield f"data: {json.dumps({'type': 'status', 'content': 'Khởi động Pipeline...'})}\n\n"
                
                initial_state = {
                    "user_prompt": req.message,
                    "user_motivation": "",
                    "messages": [],
                    "dashboard_blueprint": None,
                    "dashboard_sections": [],
                    "current_section_index": 0,
                    "raw_data": None,
                    "current_section_goal": "",
                    "draft_report": ""
                }
                
                async for event in agent_graph.astream(initial_state, config=config):
                    node_name = list(event.keys())[0]
                    node_data = event[node_name]
                    
                    yield f"data: {json.dumps({'type': 'node_finish', 'node': node_name, 'data': node_data})}\n\n"
                    await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Check if graph paused due to interrupt
            state = agent_graph.get_state(config)
            if state.next:
                yield f"data: {json.dumps({'type': 'interrupt', 'node': state.next[0]})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/stats")
async def get_dashboard_stats():
    return {
        "health": {
            "bigquery": 99.9,
            "agent_core_nodes": 14,
            "latency_ms": random.randint(18, 35)
        },
        "tasks": [
            {"id": "#TSK-091", "type": "Data Sync", "status": "Completed", "time": "2m ago"},
            {"id": "#TSK-092", "type": "Model Retrain", "status": "In Progress", "time": "15m ago"},
            {"id": "#TSK-093", "type": "Anomaly Detect", "status": "Failed", "time": "1h ago"}
        ],
        "alerts": [
            {"title": "High CPU Usage", "desc": "Node cluster Alpha is operating at 92% capacity."},
            {"title": "Pipeline Delay", "desc": "Ingestion queue for stream-B is lagging behind expected SLA."}
        ],
        "resources": {
            "compute": random.randint(60, 85),
            "memory": random.randint(40, 60),
            "storage": 90
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
