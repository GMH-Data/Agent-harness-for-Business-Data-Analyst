# Hướng dẫn Deploy AI RISSER lên Google Cloud Run

Đây là tài liệu hướng dẫn chi tiết từng bước để đẩy hệ thống của bạn lên Google Cloud Run.

## Bước 1: Chuẩn bị Supabase
1. Đăng nhập [Supabase](https://supabase.com/).
2. Tạo 1 Project.
3. Vào **Settings > Database** để lấy Connection String.
4. Mở file `superset/superset_config.py` và dán Connection String đó vào biến `SQLALCHEMY_DATABASE_URI`. 
   > Lưu ý: Nhớ thay `[PASSWORD_CỦA_BẠN]` bằng mật khẩu bạn đã tạo.
5. Copy file `gcp_key.json` từ thư mục `Key/` của bạn vào thư mục `cloud_deploy/superset/` để lát nữa Docker có thể copy nó vào image.

## Bước 2: Cài đặt và Đăng nhập Google Cloud SDK
1. Cài đặt `gcloud` CLI nếu chưa có.
2. Mở terminal và chạy lệnh:
   ```bash
   gcloud auth login
   gcloud config set project [TÊN_PROJECT_ID_CỦA_BẠN]
   # Ví dụ: gcloud config set project ai-riser-505908
   ```

## Bước 3: Build và Deploy Superset lên Cloud Run
Chạy lần lượt 2 lệnh sau trong thư mục `cloud_deploy/superset/`:

```bash
cd cloud_deploy/superset

# 1. Build Docker image và đẩy lên Google Container Registry
gcloud builds submit --tag gcr.io/[TÊN_PROJECT_ID_CỦA_BẠN]/superset

# 2. Deploy lên Cloud Run
gcloud run deploy airisser-superset \
  --image gcr.io/[TÊN_PROJECT_ID_CỦA_BẠN]/superset \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8080
```
Sau khi lệnh chạy xong, Google sẽ trả về một link URL (ví dụ: `https://airisser-superset-xxx.a.run.app`). Đó là trang Superset của bạn! Đăng nhập bằng `admin` / `admin`.

## Bước 4: Cập nhật URL và Deploy Agent Core
1. Mở file `.env` (hoặc file cấu hình nơi chứa `SUPERSET_URL`) và sửa lại `SUPERSET_URL` thành link URL mới mà Google vừa cấp.
2. Chạy lệnh sau trong thư mục gốc của project (nơi chứa thư mục `agent_core`):

```bash
# Đứng ở thư mục gốc của project AI RISSER, KHÔNG phải trong cloud_deploy
# (Vì Dockerfile của Agent cần đọc thư mục agent_core và requirements.txt ở root)

# 1. Build image
gcloud builds submit --tag gcr.io/[TÊN_PROJECT_ID_CỦA_BẠN]/agent-core -f cloud_deploy/agent_core/Dockerfile .

# 2. Deploy lên Cloud Run
gcloud run deploy airisser-agent \
  --image gcr.io/[TÊN_PROJECT_ID_CỦA_BẠN]/agent-core \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --port 8080
```

Xong! Bạn đã hoàn thành việc đưa toàn bộ hệ thống (trừ Airflow không cấp bách) lên Google Cloud với chi phí gần như bằng 0 (Free Tier).
