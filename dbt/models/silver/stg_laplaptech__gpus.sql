select
    cast(id as int64) as gpu_model_id,
    cast(name as string) as gpu_name,
    cast(brand_id as int64) as brand_id,
    cast(is_active as boolean) as is_active,
    timestamp_seconds(cast(created_on / 1000000000 as int64)) as created_on,
    timestamp_seconds(cast(changed_on / 1000000000 as int64)) as changed_on,
    timestamp_seconds(cast(elton_created_at / 1000000000 as int64)) as elton_created_at
from {{ source('laplaptech_raw', 'raw_gpu_model') }}
