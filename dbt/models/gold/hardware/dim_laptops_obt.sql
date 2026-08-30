select
    l.laptop_model_id,
    l.laptop_name,
    b_lap.brand_name as laptop_brand,
    l.is_gaming_laptop,
    l.is_workstation,
    l.is_mobile_device,
    l.year_introduce,
    
    # Thông tin CPU
    cpu.cpu_name,
    b_cpu.brand_name as cpu_brand,
    l.cpu_tdp,
    l.cpu_note,
    
    # Thông tin GPU
    gpu.gpu_name,
    b_gpu.brand_name as gpu_brand,
    l.gpu_tdp,
    l.gpu_note,
    
    # Thuộc tính phần cứng khác
    l.battery_capacity_whr,
    l.screen_size,
    l.screen_dimension_width,
    l.screen_dimension_height,
    l.screen_ppi,
    l.laptop_weight,
    l.charger_weight,
    l.brand_model_codename,
    l.thumbnail_image_url,
    
    # Thông tin điểm số benchmark
    bench.office_battery_result_minutes,
    bench.gaming_battery_result_minutes,
    bench.foldable_opening_battery_result_minutes,
    bench.geekbench_6_cpu_single_core_plugged_in,
    bench.geekbench_6_cpu_single_core_battery,
    bench.geekbench_6_cpu_multi_core_plugged_in,
    bench.geekbench_6_cpu_multi_core_battery,
    bench.geekbench_6_compute_gpu_plugged_in,
    bench.geekbench_6_compute_gpu_battery,
    bench.review_video_url,
    bench.note as benchmark_note,
    
    # --- FEATURE ENGINEERING ---
    # 1. Tỷ lệ giữ hiệu năng khi chạy pin
    safe_divide(bench.geekbench_6_cpu_single_core_battery, bench.geekbench_6_cpu_single_core_plugged_in) * 100 as cpu_single_battery_retention_pct,
    safe_divide(bench.geekbench_6_cpu_multi_core_battery, bench.geekbench_6_cpu_multi_core_plugged_in) * 100 as cpu_multi_battery_retention_pct,
    safe_divide(bench.geekbench_6_compute_gpu_battery, bench.geekbench_6_compute_gpu_plugged_in) * 100 as gpu_compute_battery_retention_pct,
    
    # 2. Mobility Score
    safe_divide(bench.office_battery_result_minutes, (l.laptop_weight / 1000.0)) as mobility_score
    
from {{ ref('stg_laplaptech__laptops') }} l
left join {{ ref('stg_laplaptech__brands') }} b_lap on l.brand_id = b_lap.brand_id
left join {{ ref('stg_laplaptech__cpus') }} cpu on l.cpu_model_id = cpu.cpu_model_id
left join {{ ref('stg_laplaptech__brands') }} b_cpu on cpu.brand_id = b_cpu.brand_id
left join {{ ref('stg_laplaptech__gpus') }} gpu on l.gpu_model_id = gpu.gpu_model_id
left join {{ ref('stg_laplaptech__brands') }} b_gpu on gpu.brand_id = b_gpu.brand_id
left join {{ ref('stg_laplaptech__benchmarks') }} bench on l.laptop_model_id = bench.laptop_model_id
where l.is_active = true
