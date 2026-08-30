FROM apache/airflow:2.9.3-python3.10

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir \
    clickhouse-connect==0.7.16 \
    pandas==2.2.2 \
    pyarrow==16.1.0 \
    dbt-bigquery==1.8.2
