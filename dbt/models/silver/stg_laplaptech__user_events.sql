select
    cast(id as int64) as event_id,
    cast(event_name as string) as event_name,
    cast(user_id as int64) as user_id,
    cast(user_psuedo_id as string) as user_pseudo_id,
    cast(session_id as string) as session_id,
    cast(app_version as string) as app_version,
    
    # Bóc tách trường JSON event_data
    JSON_VALUE(event_data, '$.page_name') as page_name,
    cast(JSON_VALUE(event_data, '$.device_id') as int64) as laptop_model_id,
    JSON_VALUE(event_data, '$.url') as url,
    JSON_VALUE(event_data, '$.referrer') as referrer,
    
    # Bóc tách trường JSON device
    JSON_VALUE(device, '$.user_agent') as user_agent,
    JSON_VALUE(device, '$.os_name') as os_name,
    JSON_VALUE(device, '$.os_version') as os_version,
    JSON_VALUE(device, '$.device_brand') as device_brand,
    JSON_VALUE(device, '$.device_name') as device_name,
    JSON_VALUE(device, '$.device_type') as device_type,
    
    # Ép kiểu dữ liệu thời gian
    TIMESTAMP_SECONDS(cast(event_local_timestamp as int64)) as event_timestamp,
    cast(event_date as date) as event_date,
    timestamp_seconds(cast(elton_created_at / 1000000000 as int64)) as elton_created_at
from {{ source('laplaptech_raw', 'raw_user_event_tracking') }}
