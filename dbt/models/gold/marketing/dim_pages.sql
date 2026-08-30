with unique_pages as (
    select distinct 
        url,
        page_name
    from {{ ref('stg_laplaptech__user_events') }}
    where url is not null
)
select
    farm_fingerprint(url) as page_key,
    url,
    page_name,
    case 
        when url = 'https://laplap.tech/' then 'Home'
        when url like '%/device/%' then 'Device Detail'
        when url like '%/compare%' then 'Comparison'
        else 'Other'
    end as page_type
from unique_pages
