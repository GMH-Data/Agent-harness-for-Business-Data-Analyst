with session_events as (
    select 
        session_id,
        min(event_timestamp) as session_start_timestamp,
        max(event_timestamp) as session_end_timestamp,
        count(event_id) as total_events
    from {{ ref('stg_laplaptech__user_events') }}
    group by session_id
)
select
    session_id,
    session_start_timestamp,
    session_end_timestamp,
    timestamp_diff(session_end_timestamp, session_start_timestamp, second) as session_duration_seconds,
    total_events,
    case when total_events = 1 then true else false end as is_bounce_session
from session_events
