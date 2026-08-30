# Kế hoạch triển khai Step 3: Local dbt Modeling (Bronze -> Silver -> Gold)

Tài liệu này chi tiết hóa thiết kế kỹ thuật, mô hình hóa dữ liệu và kế hoạch thực thi để xây dựng toàn bộ hệ thống dbt models trên GCP BigQuery.

## Mục tiêu (Goal)
Hoàn thiện toàn bộ các tầng chuyển đổi dữ liệu của dự án Laplaptech bằng dbt:
1. **Bronze Layer (Sources)**: Khai báo 6 bảng thô BigQuery nạp từ ClickHouse làm nguồn đầu vào.
2. **Silver Layer (Staging & Clean)**: 
   - Parse các chuỗi JSON phức tạp trong `raw_user_event_tracking` (các cột `event_data` và `device`) thành các cột riêng biệt bằng hàm BigQuery `JSON_VALUE`.
   - Chuẩn hóa kiểu dữ liệu số, ép kiểu ngày tháng, và thực hiện khử trùng (deduplication) dữ liệu benchmark laptop để lấy bản ghi mới nhất.
3. **Gold Layer (OBT & Kimball Star Schema)**:
   - **OBT (One Big Table)**: Tạo bảng phẳng `dim_laptops_obt` chứa đầy đủ cấu hình laptop, CPU, GPU cùng các trường review text gộp phục vụ RAG.
   - **Kimball Star Schema**: Tạo Fact `fct_user_event_tracking` được phân vùng (partition) và gom cụm (cluster) tối ưu, liên kết với các bảng Dimension (`dim_pages`, `dim_sessions`, `dim_devices`, `dim_traffic_sources`).

---

## Phân tích Chi tiết Tầng chuyển đổi (dbt Layers Design)

### 1. Bronze Layer (Sources)
Khai báo nguồn dữ liệu thô `laplaptech_raw` trong `dbt/models/bronze/sources.yml`.

### 2. Silver Layer (Staging)
* **`stg_laplaptech__brands`**: Chọn các cột cần thiết từ `raw_brand`, đưa kiểu dữ liệu Nullable sang dạng chuẩn.
* **`stg_laplaptech__cpus`**: Chọn từ `raw_cpu_model`.
* **`stg_laplaptech__gpus`**: Chọn từ `raw_gpu_model`.
* **`stg_laplaptech__laptops`**: Chọn từ `raw_laptop_model`.
* **`stg_laplaptech__benchmarks`**: Khử trùng dữ liệu benchmark của cùng một `laptop_model_id` bằng hàm `ROW_NUMBER() OVER (PARTITION BY laptop_model_id ORDER BY changed_on DESC, id DESC)` để chỉ giữ lại 1 bài test mới nhất cho mỗi máy.
* **`stg_laplaptech__user_events`**: 
  - Đọc từ `raw_user_event_tracking`.
  - Sử dụng `JSON_VALUE(event_data, '$.page_name')`, `JSON_VALUE(event_data, '$.device_id')`, `JSON_VALUE(event_data, '$.url')`, `JSON_VALUE(event_data, '$.referrer')` để phân tách dữ liệu sự kiện.
  - Sử dụng `JSON_VALUE(device, '$.user_agent')`, `JSON_VALUE(device, '$.os_name')`, `JSON_VALUE(device, '$.os_version')`, `JSON_VALUE(device, '$.device_type')` để trích xuất thông tin thiết bị client.
  - Ép kiểu `TIMESTAMP_SECONDS(event_local_timestamp)` và trích xuất `event_date` (phân vùng chính).

### 3. Gold Layer (Marts)
#### Domain 1: Hardware & Performance (OBT)
* **`dim_laptops_obt`**: Thực hiện JOIN các bảng Silver: `stg_laplaptech__laptops` làm gốc, JOIN với `stg_laplaptech__brands` (cho laptop brand), `stg_laplaptech__cpus` & `stg_laplaptech__gpus` kèm brand tương ứng, và cuối cùng `LEFT JOIN` với bảng benchmark đã khử trùng `stg_laplaptech__benchmarks`.
* **Feature Engineering**:
  - `cpu_single_battery_retention_pct`: `(geekbench_6_cpu_single_core_battery / geekbench_6_cpu_single_core_plugged_in) * 100`
  - `cpu_multi_battery_retention_pct`: `(geekbench_6_cpu_multi_core_battery / geekbench_6_cpu_multi_core_plugged_in) * 100`
  - `gpu_compute_battery_retention_pct`: `(geekbench_6_compute_gpu_battery / geekbench_6_compute_gpu_plugged_in) * 100`
  - `mobility_score`: `office_battery_result_minutes / (laptop_weight / 1000.0)`
  - `semantic_text_chunk`: Chuỗi văn bản mô tả cấu hình ghép từ các cột phục vụ LLM RAG.

#### Domain 2: Clickstream & SEO (Kimball Star Schema)
* **`dim_pages`**: Trích xuất các URL và Page Name duy nhất từ Silver events, sử dụng `FARM_FINGERPRINT(url)` để sinh ra khóa chính đại diện `page_id`.
* **`dim_devices`**: Phân nhóm cấu hình thiết bị duy nhất (`os_name`, `device_type`, `user_agent`), sinh `device_id` bằng `FARM_FINGERPRINT`.
* **`dim_sessions`**: Tổng hợp thông tin từ events theo `session_id`, tính toán thời lượng phiên, cờ `is_bounce_session` (nếu session chỉ có 1 event).
* **`fct_user_event_tracking`**: Bảng Fact lưu giữ các dòng sự kiện tracking của người dùng, liên kết khóa ngoại với các Dimension qua `page_id`, `device_id`, `session_id`, `laptop_model_id`. Được cấu hình **Partition by `event_date`** và **Cluster by `event_name` & `laptop_model_id`** trên BigQuery.

---

## Proposed Changes

```mermaid
graph TD
    subgraph Bronze Layer
        A[raw_brand]
        B[raw_cpu_model]
        C[raw_gpu_model]
        D[raw_laptop_model]
        E[raw_laptop_benchmark_result]
        F[raw_user_event_tracking]
    end
    
    subgraph Silver Layer
        A --> stg_brands[stg_laplaptech__brands]
        B --> stg_cpus[stg_laplaptech__cpus]
        C --> stg_gpus[stg_laplaptech__gpus]
        D --> stg_laptops[stg_laplaptech__laptops]
        E --> stg_benchmarks[stg_laplaptech__benchmarks]
        F --> stg_events[stg_laplaptech__user_events]
    end
    
    subgraph Gold Layer (Marts)
        stg_laptops & stg_brands & stg_cpus & stg_gpus & stg_benchmarks --> dim_laptops_obt
        
        stg_events --> dim_pages
        stg_events --> dim_devices
        stg_events --> dim_sessions
        stg_events & dim_pages & dim_devices & dim_sessions --> fct_user_event_tracking
    end
```

### 1. Bronze Layer Configuration
#### [NEW] dbt/models/bronze/sources.yml
Khai báo nguồn dữ liệu thô:

```yaml
version: 2

sources:
  - name: laplaptech_raw
    database: ai-riser-505908
    schema: laplaptech_raw
    tables:
      - name: raw_brand
      - name: raw_cpu_model
      - name: raw_gpu_model
      - name: raw_laptop_model
      - name: raw_laptop_benchmark_result
      - name: raw_user_event_tracking
```

### 2. Silver Layer Models
#### [NEW] dbt/models/silver/stg_laplaptech__brands.sql
```sql
select
    cast(id as int64) as brand_id,
    cast(name as string) as brand_name,
    cast(is_chip_brand as boolean) as is_chip_brand,
    cast(created_on as timestamp) as created_on,
    cast(changed_on as timestamp) as changed_on,
    cast(elton_created_at as timestamp) as elton_created_at
from {{ source('laplaptech_raw', 'raw_brand') }}
```

#### [NEW] dbt/models/silver/stg_laplaptech__cpus.sql
```sql
select
    cast(id as int64) as cpu_model_id,
    cast(name as string) as cpu_name,
    cast(brand_id as int64) as brand_id,
    cast(is_active as boolean) as is_active,
    cast(created_on as timestamp) as created_on,
    cast(changed_on as timestamp) as changed_on,
    cast(elton_created_at as timestamp) as elton_created_at
from {{ source('laplaptech_raw', 'raw_cpu_model') }}
```

#### [NEW] dbt/models/silver/stg_laplaptech__gpus.sql
```sql
select
    cast(id as int64) as gpu_model_id,
    cast(name as string) as gpu_name,
    cast(brand_id as int64) as brand_id,
    cast(is_active as boolean) as is_active,
    cast(created_on as timestamp) as created_on,
    cast(changed_on as timestamp) as changed_on,
    cast(elton_created_at as timestamp) as elton_created_at
from {{ source('laplaptech_raw', 'raw_gpu_model') }}
```

#### [NEW] dbt/models/silver/stg_laplaptech__laptops.sql
```sql
select
    cast(id as int64) as laptop_model_id,
    cast(name as string) as laptop_name,
    cast(brand_id as int64) as brand_id,
    cast(cpu_model_id as int64) as cpu_model_id,
    cast(gpu_model_id as int64) as gpu_model_id,
    cast(is_gaming_laptop as boolean) as is_gaming_laptop,
    cast(is_workstation as boolean) as is_workstation,
    cast(is_mobile_device as boolean) as is_mobile_device,
    cast(is_visible as boolean) as is_visible,
    cast(is_active as boolean) as is_active,
    cast(year_introduce as int64) as year_introduce,
    cast(cpu_note as string) as cpu_note,
    cast(cpu_tdp as string) as cpu_tdp,
    cast(gpu_note as string) as gpu_note,
    cast(gpu_tdp as string) as gpu_tdp,
    cast(battery_capacity_whr as float64) as battery_capacity_whr,
    cast(screen_size as float64) as screen_size,
    cast(screen_dimension_width as float64) as screen_dimension_width,
    cast(screen_dimension_height as float64) as screen_dimension_height,
    cast(screen_ppi as float64) as screen_ppi,
    cast(laptop_weight as float64) as laptop_weight,
    cast(charger_weight as float64) as charger_weight,
    cast(brand_model_codename as string) as brand_model_codename,
    cast(thumbnail_image_url as string) as thumbnail_image_url,
    cast(created_on as timestamp) as created_on,
    cast(changed_on as timestamp) as changed_on,
    cast(elton_created_at as timestamp) as elton_created_at
from {{ source('laplaptech_raw', 'raw_laptop_model') }}
```

#### [NEW] dbt/models/silver/stg_laplaptech__benchmarks.sql
```sql
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
    cast(created_on as timestamp) as created_on,
    cast(changed_on as timestamp) as changed_on,
    cast(elton_created_at as timestamp) as elton_created_at
from deduplicated_benchmarks
where rn = 1
```

#### [NEW] dbt/models/silver/stg_laplaptech__user_events.sql
```sql
select
    cast(id as int64) as event_id,
    cast(event_name as string) as event_name,
    cast(user_id as int64) as user_id,
    cast(user_psuedo_id as string) as user_pseudo_id,
    cast(session_id as string) as session_id,
    cast(app_version as string) as app_version,
    
    # Bóc tách trường JSON event_data
    JSON_VALUE(event_data, '$.page_name') as page_name,
    cast(JSON_VALUE(event_data, '$.device_id') as int64) as laptop_model_id, -- Khóa liên kết với laptop_model
    JSON_VALUE(event_data, '$.url') as url,
    JSON_VALUE(event_data, '$.referrer') as referrer,
    
    # Bóc tách trường JSON device
    JSON_VALUE(device, '$.user_agent') as user_agent,
    JSON_VALUE(device, '$.os_name') as os_name,
    JSON_VALUE(device, '$.os_version') as os_version,
    JSON_VALUE(device, '$.device_brand') as device_brand,
    JSON_VALUE(device, '$.device_name') as device_name,
    JSON_VALUE(device, '$.device_type') as device_type,
    
    # Ép kiểu dữ liệu thời gian (event_local_timestamp là UNIX timestamp tính bằng giây)
    TIMESTAMP_SECONDS(cast(event_local_timestamp as int64)) as event_timestamp,
    cast(event_date as date) as event_date,
    cast(elton_created_at as timestamp) as elton_created_at
from {{ source('laplaptech_raw', 'raw_user_event_tracking') }}
```

### 3. Gold Layer Models
#### [NEW] dbt/models/gold/dim_laptops_obt.sql
```sql
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
    
    # Thông tin điểm số benchmark (Từ bảng đã khử trùng)
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
    
    # 2. Mobility Score (Thời lượng pin văn phòng (phút) / Trọng lượng (kg))
    # Trọng lượng laptop_weight trong ClickHouse được lưu bằng đơn vị gram
    safe_divide(bench.office_battery_result_minutes, (l.laptop_weight / 1000.0)) as mobility_score,
    
    # 3. Gộp khối văn bản review làm Metadata phục vụ RAG AI
    concat(
        'Laptop Model: ', l.name, '. ',
        'Brand: ', b_lap.brand_name, '. ',
        'CPU: ', cpu.cpu_name, ' (TDP: ', coalesce(l.cpu_tdp, 'N/A'), '). ',
        'GPU: ', gpu.gpu_name, ' (TDP: ', coalesce(l.gpu_tdp, 'N/A'), '). ',
        'Battery: ', coalesce(cast(l.battery_capacity_whr as string), 'N/A'), ' Wh. ',
        'Weight: ', coalesce(cast(l.laptop_weight / 1000.0 as string), 'N/A'), ' kg. ',
        'CPU Note: ', coalesce(l.cpu_note, 'None'), '. ',
        'GPU Note: ', coalesce(l.gpu_note, 'None'), '. ',
        'Benchmark Note: ', coalesce(bench.note, 'None'), '.'
    ) as semantic_text_chunk
    
from {{ ref('stg_laplaptech__laptops') }} l
left join {{ ref('stg_laplaptech__brands') }} b_lap on l.brand_id = b_lap.brand_id
left join {{ ref('stg_laplaptech__cpus') }} cpu on l.cpu_model_id = cpu.cpu_model_id
left join {{ ref('stg_laplaptech__brands') }} b_cpu on cpu.brand_id = b_cpu.brand_id
left join {{ ref('stg_laplaptech__gpus') }} gpu on l.gpu_model_id = gpu.gpu_model_id
left join {{ ref('stg_laplaptech__brands') }} b_gpu on gpu.brand_id = b_gpu.brand_id
left join {{ ref('stg_laplaptech__benchmarks') }} bench on l.laptop_model_id = bench.laptop_model_id
where l.is_active = true
```

#### [NEW] dbt/models/gold/dim_pages.sql
```sql
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
```

#### [NEW] dbt/models/gold/dim_devices.sql
```sql
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
```

#### [NEW] dbt/models/gold/dim_sessions.sql
```sql
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
```

#### [NEW] dbt/models/gold/fct_user_event_tracking.sql
```sql
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
```

---

## Verification Plan

### Automated Tests
Thực thi kiểm tra cấu trúc cú pháp dbt cục bộ trong container:
```bash
docker-compose exec -T -u airflow airflow-scheduler bash -c "export PATH=/home/airflow/.local/bin:\$PATH && dbt run --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt"
```
*Kết quả mong đợi: `Completed successfully (11 models built)`.*

### Manual Verification
1. Dùng console BigQuery kiểm tra xem cấu trúc dữ liệu của bảng `dim_laptops_obt` có đầy đủ các cột suy hao pin và semantic chunk cho RAG hay không.
2. Kiểm tra schema phân vùng và gom cụm của `fct_user_event_tracking` trên BigQuery.
