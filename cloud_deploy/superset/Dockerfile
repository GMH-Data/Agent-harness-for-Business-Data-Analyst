FROM apache/superset:3.1.0

# Chuyển sang user root để cài đặt thư viện cần thiết
USER root

# Cài đặt driver kết nối PostgreSQL và BigQuery
RUN pip install psycopg2-binary sqlalchemy-bigquery google-cloud-bigquery

# Tạo thư mục Key
RUN mkdir -p /app/Key

# Copy file cấu hình và start script vào container
COPY superset_config.py /app/pythonpath/superset_config.py
COPY start.sh /app/start.sh

# Chú ý: File gcp_key.json phải được copy từ thư mục gốc của project vào đây khi build
COPY gcp_key.json /app/Key/gcp_key.json

# Cấp quyền
RUN chmod -R 777 /app/Key
RUN chmod +x /app/start.sh

USER superset

# Khởi tạo db và tạo admin mặc định khi chạy container
ENTRYPOINT ["/app/start.sh"]
