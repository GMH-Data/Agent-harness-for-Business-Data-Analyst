import sys
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Cấp quyền import module agent_core từ thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_core.graph import app as graph_app
import langfuse
from langfuse.decorators import langfuse_context

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            user_input = data.get("message", "")
            thread_id = data.get("thread_id", "html_test_1")
            
            # Streaming Response
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'close')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('X-Accel-Buffering', 'no')
            self.end_headers()
            
            config = {"configurable": {"thread_id": thread_id}, "run_name": "web_tester"}
            
            langfuse_context.update_current_trace(
                name="AI_RISSER_Web_Test",
                session_id="html_test_1",
                tags=["web", "langgraph", "phase_2", "hitl"]
            )
            
            # Khởi tạo hoặc ghi log User Request
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
            os.makedirs(log_path, exist_ok=True)
            with open(os.path.join(log_path, f"{thread_id}.log"), "a", encoding="utf-8") as f:
                import datetime
                f.write(f"\n======================================================\n")
                f.write(f"[{datetime.datetime.now().isoformat()}] USER REQUEST / HITL ACTION: {user_input}\n")
                f.write(f"======================================================\n\n")
            
            try:
                # Kiểm tra xem graph có đang bị tạm dừng (interrupt) không
                current_state = graph_app.get_state(config)
                
                if current_state.next:
                    # Nếu đang dừng, nhận phản hồi HITL từ user (approve, reject, subtask)
                    graph_app.update_state(config, {"hitl_response": user_input})
                    stream_generator = graph_app.stream(None, config=config, stream_mode=["updates", "debug"])
                else:
                    # Nếu không, bắt đầu luồng mới
                    full_state = {"user_prompt": user_input, "task_id": "html_test_1"}
                    stream_generator = graph_app.stream(full_state, config=config, stream_mode=["updates", "debug"])
                
                for chunk in stream_generator:
                    mode, payload = chunk
                    if mode == "debug" and payload.get("type") == "task":
                        node_name = payload.get("payload", {}).get("name", "Unknown Node")
                        if node_name != "Unknown Node":
                            # Ghi log ra file
                            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                            os.makedirs(log_path, exist_ok=True)
                            with open(os.path.join(log_path, f"{thread_id}.log"), "a", encoding="utf-8") as f:
                                import datetime
                                f.write(f"[{datetime.datetime.now().isoformat()}] BẮT ĐẦU CHẠY: {node_name}\n")
                            
                            msg = json.dumps({"type": "status", "content": f"⏳ Đang chạy: {node_name}..."})
                            self.wfile.write(f"data: {msg}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            
                    elif mode == "updates":
                        for node_name, node_update in payload.items():
                            if node_name == "__interrupt__":
                                continue
                                
                            # Gửi toàn bộ dữ liệu JSON nguyên bản để UI tự hiển thị
                            display_data = node_update if node_update is not None else {}
                            
                            # Ghi log ra file
                            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                            os.makedirs(log_path, exist_ok=True)
                            with open(os.path.join(log_path, f"{thread_id}.log"), "a", encoding="utf-8") as f:
                                import datetime
                                f.write(f"[{datetime.datetime.now().isoformat()}] NODE FINISH: {node_name}\n")
                                f.write(json.dumps(display_data, ensure_ascii=False, indent=2) + "\n\n")
                            
                            msg = json.dumps({"type": "node_finish", "node": node_name, "data": display_data})
                            self.wfile.write(f"data: {msg}\n\n".encode('utf-8'))
                            self.wfile.flush()
                
                # Sau khi stream xong, kiểm tra xem có bị dừng ở HITL không
                final_state = graph_app.get_state(config)
                if final_state.next:
                    pending_node = final_state.next[0]
                    msg = json.dumps({"type": "interrupt", "node": pending_node})
                    self.wfile.write(f"data: {msg}\n\n".encode('utf-8'))
                    self.wfile.flush()
                else:
                    self.wfile.write(f"data: {json.dumps({'type': 'done'})}\n\n".encode('utf-8'))
                    self.wfile.flush()
                    
            except Exception as e:
                msg = json.dumps({"type": "error", "content": str(e)})
                self.wfile.write(f"data: {msg}\n\n".encode('utf-8'))
                self.wfile.flush()
                
            langfuse_context.flush()

if __name__ == '__main__':
    port = 8090
    server = HTTPServer(('localhost', port), ChatHandler)
    print(f"\n=======================================================")
    print(f"🚀 AI RISSER WEB TESTER ĐÃ CHẠY TẠI: http://localhost:{port}")
    print(f"=======================================================\n")
    server.serve_forever()
