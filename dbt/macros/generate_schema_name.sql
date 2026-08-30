{#
    Macro này ghi đè logic mặc định của dbt (dbt_project.yml dataset + custom_schema_name)
    để lưu các bảng Gold trực tiếp vào dataset laplaptech_hardware hoặc laplaptech_marketing
    thay vì bị dính tiền tố target dataset (ví dụ: laplaptech_staging_hardware).
#}

{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is not none -%}

        {# 
           Nếu custom schema là hardware hoặc marketing, 
           đưa trực tiếp vào laplaptech_hardware hoặc laplaptech_marketing
        #}
        {%- if custom_schema_name in ['hardware', 'marketing'] -%}
            {{ 'laplaptech_' ~ custom_schema_name | trim }}
        {%- else -%}
            {{ default_schema ~ '_' ~ custom_schema_name | trim }}
        {%- endif -%}

    {%- else -%}

        {{ default_schema }}

    {%- endif -%}

{%- endmacro %}
