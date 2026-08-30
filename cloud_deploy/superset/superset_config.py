import os

# Secret Key bắt buộc
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "LaplaptechSuperSecretKey2026")

# Trỏ database về Supabase thay vì Local Postgres
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", 
    "postgresql://postgres.rbekvnuukcqcjwmprdyf:Phamthanhson%4023122001@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
)

# Để Cloud Run tự handle port 8080
SUPERSET_WEBSERVER_PORT = 8080
