{{ config(
    materialized='table',
    partition_by={
      "field": "event_date",
      "data_type": "date"
    },
    cluster_by=["event_name", "laptop_model_id"]
) }}

select
    event_id,
    event_name,
    user_id,
    user_pseudo_id,
    session_id,
    laptop_model_id,
    farm_fingerprint(url) as page_key,
    farm_fingerprint(user_agent) as device_key,
    event_timestamp,
    event_date
from {{ ref('stg_laplaptech__user_events') }}
