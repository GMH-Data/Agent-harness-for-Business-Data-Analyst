with unique_devices as (
    select distinct 
        user_agent,
        os_name,
        os_version,
        device_brand,
        device_name,
        device_type
    from {{ ref('stg_laplaptech__user_events') }}
    where user_agent is not null
)
select
    farm_fingerprint(user_agent) as device_key,
    user_agent,
    os_name,
    os_version,
    device_brand,
    device_name,
    device_type
from unique_devices
