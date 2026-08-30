#!/bin/bash
superset db upgrade
superset fab create-admin --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin
superset init
gunicorn --bind  0.0.0.0:8080 --workers 1 --worker-class gthread --threads 20 --timeout 120 --limit-request-line 0 --limit-request-field_size 0 "superset.app:create_app()"
