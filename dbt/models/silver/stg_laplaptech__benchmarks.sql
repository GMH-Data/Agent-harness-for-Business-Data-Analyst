with deduplicated_benchmarks as (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY laptop_model_id ORDER BY changed_on DESC, id DESC) as rn
    FROM {{ source('laplaptech_raw', 'raw_laptop_benchmark_result') }}
    WHERE is_active = true
)
select
    cast(id as int64) as benchmark_id,
    cast(laptop_model_id as int64) as laptop_model_id,
    cast(office_battery_result_minutes as float64) as office_battery_result_minutes,
    cast(gaming_battery_result_minutes as float64) as gaming_battery_result_minutes,
    cast(foldable_opening_battery_result_minutes as float64) as foldable_opening_battery_result_minutes,
    cast(geekbench_6_cpu_single_core_plugged_in as float64) as geekbench_6_cpu_single_core_plugged_in,
    cast(geekbench_6_cpu_single_core_battery as float64) as geekbench_6_cpu_single_core_battery,
    cast(geekbench_6_cpu_multi_core_plugged_in as float64) as geekbench_6_cpu_multi_core_plugged_in,
    cast(geekbench_6_cpu_multi_core_battery as float64) as geekbench_6_cpu_multi_core_battery,
    cast(geekbench_6_compute_gpu_plugged_in as float64) as geekbench_6_compute_gpu_plugged_in,
    cast(geekbench_6_compute_gpu_battery as float64) as geekbench_6_compute_gpu_battery,
    cast(review_video_url as string) as review_video_url,
    cast(note as string) as note,
    cast(is_active as boolean) as is_active,
    timestamp_seconds(cast(created_on / 1000000000 as int64)) as created_on,
    timestamp_seconds(cast(changed_on / 1000000000 as int64)) as changed_on,
    timestamp_seconds(cast(elton_created_at / 1000000000 as int64)) as elton_created_at
from deduplicated_benchmarks
where rn = 1
