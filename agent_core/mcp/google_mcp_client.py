import os
from google.cloud import bigquery

# Cài đặt biến môi trường credentials cục bộ cho GCP nếu chưa có
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/gmh/Project/AI RISSER/Key/gcp_key.json"

bq_client = bigquery.Client()

def query_bigquery(sql_query: str) -> str:
    """
    Hàm này đóng vai trò như một MCP Client (Tạm thời chạy native Python client).
    Khi hệ thống triển khai mcp-toolbox (Go binary) hoàn chỉnh, hàm này sẽ gọi qua giao thức STDIO/HTTP của MCP.
    """
    query_clean = sql_query.lower()
    log_tables = ["raw_user_event_tracking", "fct_user_event_tracking"]
    
    for table in log_tables:
        if table in query_clean:
            has_date_filter = "event_date" in query_clean
            has_laptop_filter = "laptop_model_id" in query_clean
            if not (has_date_filter or has_laptop_filter):
                return (
                    f"ERROR: Lệnh SQL truy vấn bảng log lớn `{table}` nhưng thiếu bộ lọc. "
                    "Vui lòng bổ sung WHERE event_date hoặc laptop_model_id để tránh Full Table Scan."
                )
    
    try:
        query_job = bq_client.query(sql_query)
        results = query_job.result()
        rows = [dict(row) for row in results]
        
        import json
        for row in rows:
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
        return json.dumps(rows, ensure_ascii=False)
    except Exception as e:
        return f"Database Error: {str(e)}"
