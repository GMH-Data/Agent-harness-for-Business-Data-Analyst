import io
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import clickhouse_connect
from google.cloud import bigquery

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

CH_HOST = "applog.xomdata.com"
CH_PORT = 80
CH_USER = "xomdata"
CH_PASS = "Vyljk8uhGfkR25vuocmNaJ1wJjtJ6920EANi0JkU"
CH_DB = "laplaptech"

BQ_PROJECT = "ai-riser-505908"
BQ_RAW_DATASET = "laplaptech_raw"

FULL_REFRESH_TABLES = [
    "brand",
    "cpu_model",
    "gpu_model",
    "laptop_model",
    "laptop_benchmark_result"
]

def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASS
    )

def log_audit_record(table_name, row_count, compressed_bytes, duration, status, error_msg=""):
    bq_client = bigquery.Client()
    audit_table_ref = f"{BQ_PROJECT}.{BQ_RAW_DATASET}.audit_pipeline_logs"
    
    schema = [
        bigquery.SchemaField("table_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("row_count", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("compressed_bytes", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("duration_seconds", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("elton_created_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    
    try:
        bq_client.get_table(audit_table_ref)
    except Exception:
        table = bigquery.Table(audit_table_ref, schema=schema)
        bq_client.create_table(table)
        logger.info(f"Created audit table {audit_table_ref}")
        
    row_to_insert = {
        "table_name": table_name,
        "row_count": int(row_count),
        "compressed_bytes": int(compressed_bytes),
        "duration_seconds": float(duration),
        "status": status,
        "error_message": error_msg if error_msg else None,
        "elton_created_at": datetime.utcnow().isoformat()
    }
    
    json_data = json.dumps(row_to_insert) + "\n"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    
    load_job = bq_client.load_table_from_file(
        io.BytesIO(json_data.encode("utf-8")),
        audit_table_ref,
        job_config=job_config
    )
    load_job.result()

def ingest_full_refresh_table(table_name, **kwargs):
    start_time = datetime.now()
    ch_client = get_clickhouse_client()
    bq_client = bigquery.Client()
    
    try:
        logger.info(f"Starting Ingest (Full Refresh): {table_name}")
        df = ch_client.query_df(f"SELECT * FROM `{CH_DB}`.`{table_name}`")
        row_count = len(df)
        
        table = pa.Table.from_pandas(df)
        buf = io.BytesIO()
        pq.write_table(table, buf, compression="SNAPPY")
        parquet_data = buf.getvalue()
        compressed_bytes = len(parquet_data)
        
        table_ref = f"{BQ_PROJECT}.{BQ_RAW_DATASET}.raw_{table_name}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        
        load_job = bq_client.load_table_from_file(
            io.BytesIO(parquet_data),
            table_ref,
            job_config=job_config
        )
        load_job.result()
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Ingested {row_count} rows for raw_{table_name} in {duration}s")
        
        log_audit_record(table_name, row_count, compressed_bytes, duration, "SUCCESS")
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Failed to ingest {table_name}: {str(e)}")
        log_audit_record(table_name, 0, 0, duration, "FAILED", str(e))
        raise e

# Thêm schema tĩnh cho table user_event_tracking để xử lý chính xác khi DataFrame rỗng
USER_EVENT_TRACKING_PYARROW_SCHEMA = pa.schema([
    ('id', pa.int64()),
    ('event_name', pa.string()),
    ('user_id', pa.int64()),
    ('event_data', pa.string()),
    ('device', pa.string()),
    ('event_local_timestamp', pa.int64()),
    ('event_received_on_server_timestamp', pa.int64()),
    ('session_id', pa.string()),
    ('user_psuedo_id', pa.string()),
    ('app_version', pa.string()),
    ('elton_created_at', pa.int64()),  # Nanosecond timestamp từ nguồn ClickHouse
    ('event_date', pa.date32())        # Cột phân vùng ngày
])

def ingest_incremental_tracking(ds, **kwargs):
    start_time = datetime.now()
    ch_client = get_clickhouse_client()
    bq_client = bigquery.Client()
    
    try:
        logger.info(f"Starting Ingest (Incremental) for user_event_tracking on date: {ds}")
        query = f"""
        SELECT *, toDate(event_received_on_server_timestamp) as event_date 
        FROM `{CH_DB}`.`user_event_tracking` 
        WHERE toDate(event_received_on_server_timestamp) = '{ds}'
        """
        df = ch_client.query_df(query)
        row_count = len(df)
        
        if row_count > 0:
            df["event_date"] = pd.to_datetime(df["event_date"]).dt.date
            df = df.astype({
                'id': 'Int64',
                'event_name': 'string',
                'user_id': 'Int64',
                'event_data': 'string',
                'device': 'string',
                'event_local_timestamp': 'Int64',
                'event_received_on_server_timestamp': 'Int64',
                'session_id': 'string',
                'user_psuedo_id': 'string',
                'app_version': 'string',
            })
            table = pa.Table.from_pandas(df, schema=USER_EVENT_TRACKING_PYARROW_SCHEMA)
        else:
            # Tạo bảng rỗng với cấu trúc schema chuẩn tĩnh
            table = pa.Table.from_batches([], schema=USER_EVENT_TRACKING_PYARROW_SCHEMA)
            
        buf = io.BytesIO()
        pq.write_table(table, buf, compression="SNAPPY")
        parquet_data = buf.getvalue()
        compressed_bytes = len(parquet_data)
        
        table_ref = f"{BQ_PROJECT}.{BQ_RAW_DATASET}.raw_user_event_tracking"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="event_date"
            )
        )
        
        load_job = bq_client.load_table_from_file(
            io.BytesIO(parquet_data),
            table_ref,
            job_config=job_config
        )
        load_job.result()
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Ingested {row_count} rows for raw_user_event_tracking on {ds} in {duration}s")
        
        log_audit_record("user_event_tracking", row_count, compressed_bytes, duration, "SUCCESS")
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Failed to ingest user_event_tracking on {ds}: {str(e)}")
        log_audit_record("user_event_tracking", 0, 0, duration, "FAILED", str(e))
        raise e

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "clickhouse_to_bigquery_bronze",
    default_args=default_args,
    description="Pipeline kéo dữ liệu từ ClickHouse sang GCP BigQuery Bronze Dataset",
    schedule_interval="0 1 * * *",
    start_date=datetime(2025, 1, 14),
    catchup=False,
    max_active_runs=1,
    tags=["bronze", "ingestion", "laplaptech"]
) as dag:

    tasks_full_refresh = []
    for table in FULL_REFRESH_TABLES:
        task = PythonOperator(
            task_id=f"ingest_{table}",
            python_callable=ingest_full_refresh_table,
            op_kwargs={"table_name": table}
        )
        tasks_full_refresh.append(task)
        
    task_incremental_tracking = PythonOperator(
        task_id="ingest_user_event_tracking",
        python_callable=ingest_incremental_tracking,
        op_kwargs={"ds": "{{ ds }}"}
    )

    task_dbt_run = BashOperator(
        task_id="dbt_run_transformations",
        bash_command=(
            "export PATH=/home/airflow/.local/bin:$PATH && "
            "dbt run --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt"
        )
    )

    # Thiết lập luồng phụ thuộc
    for t_refresh in tasks_full_refresh:
        t_refresh >> task_dbt_run
        
    task_incremental_tracking >> task_dbt_run
