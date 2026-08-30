FROM python:3.10-slim

WORKDIR /app

# Copy thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn
COPY agent_core/ ./agent_core/
COPY env.prod .env

# Nếu agent expose ra API (ví dụ FastAPI), expose port 8080
EXPOSE 8080

# Chạy app (thay đổi file chạy tùy vào cách bạn thiết kế server)
CMD ["python", "-m", "agent_core.api"] 
