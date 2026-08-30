FROM apache/superset:latest

USER root
# Install BigQuery SQLAlchemy driver
RUN /app/.venv/bin/python -m ensurepip --upgrade && \
    /app/.venv/bin/python -m pip install sqlalchemy-bigquery google-cloud-bigquery

USER superset
