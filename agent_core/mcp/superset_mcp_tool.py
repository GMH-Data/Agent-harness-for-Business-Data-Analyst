import os
import requests
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Superset API Server")

# Cấu hình từ môi trường hoặc mặc định
SUPERSET_URL = os.environ.get("SUPERSET_URL", "http://localhost:8088")
USERNAME = os.environ.get("SUPERSET_USERNAME", "admin")
PASSWORD = os.environ.get("SUPERSET_PASSWORD", "admin")


def get_authenticated_session() -> requests.Session:
    """Lấy Session đã được xác thực JWT và có CSRF Token kèm Cookie."""
    session = requests.Session()
    
    # 1. Lấy JWT Access Token
    url = f"{SUPERSET_URL}/api/v1/security/login"
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "provider": "db"
    }
    try:
        login_res = session.post(url, json=payload, timeout=10)
        if login_res.status_code == 200:
            token = login_res.json().get("access_token", "")
            session.headers.update({"Authorization": f"Bearer {token}"})
            
            # 2. Lấy CSRF Token (Cần truyền cookie từ session)
            csrf_res = session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
            if csrf_res.status_code == 200:
                csrf_token = csrf_res.json().get("result")
                session.headers.update({"X-CSRFToken": csrf_token})
                
            return session
    except Exception as e:
        print(f"Lỗi kết nối Superset Auth: {e}")
    return None


@mcp.tool()
def get_dashboard_link(dashboard_slug: str) -> str:
    """Trả về liên kết trực tiếp tới dashboard cụ thể trên Apache Superset."""
    return f"{SUPERSET_URL}/superset/dashboard/{dashboard_slug}/"


import re

def _validate_and_fix_metrics(metrics: list, groupby: list, chart_type: str) -> list:
    """
    QA Validator: Kiểm tra và sửa metrics trước khi đẩy vào Superset.
    
    Quy tắc:
    1. Nếu metric đã chứa hàm aggregate (COUNT, SUM, AVG, MAX, MIN, APPROX_COUNT_DISTINCT)
       → Giữ nguyên
    2. Nếu metric là bare column name (vd: "session_duration_seconds")
       → Bọc bằng SUM() cho số, COUNT() cho text
    3. Nếu metric trùng với một cột trong groupby
       → Loại bỏ khỏi metrics (tránh duplicate label)
    """
    AGGREGATE_PATTERN = re.compile(
        r'\b(COUNT|SUM|AVG|MAX|MIN|APPROX_COUNT_DISTINCT|SAFE_DIVIDE|ROUND|CAST)\s*\(',
        re.IGNORECASE
    )
    
    fixed = []
    for m in metrics:
        sql_expr = m if isinstance(m, str) else m.get("sqlExpression", "")
        label = m if isinstance(m, str) else m.get("label", sql_expr)
        
        # Rule 3: Skip if metric is same as a groupby column
        if sql_expr in groupby:
            continue
            
        # Rule 1: Already has aggregate → keep as-is
        if AGGREGATE_PATTERN.search(sql_expr):
            fixed.append(m)
            continue
        
        # Rule 2: Bare column → wrap with SUM()
        wrapped_expr = f"SUM({sql_expr})"
        wrapped_label = f"SUM({label})"
        
        if isinstance(m, str):
            fixed.append(wrapped_expr)
        else:
            fixed.append({
                "expressionType": "SQL",
                "sqlExpression": wrapped_expr,
                "label": wrapped_label
            })
    
    return fixed


@mcp.tool()
def create_draft_dashboard(dashboard_name: str, sections: List[Dict[str, Any]]) -> str:
    """
    Tạo một Dashboard Draft trên Superset thông qua REST API.
    """
    session = get_authenticated_session()
    if not session:
        return "Error: Không thể xác thực với Superset. Vui lòng kiểm tra lại cấu hình."
    
    session.headers.update({"Content-Type": "application/json"})
    
    chart_mappings = []
    # 1. Tạo các Charts
    for section in sections:
        config = section.get("chart_config", {})
        if not config or "No Data" in config.get("chart_name", ""):
            continue
            
        import json
        
        raw_metrics = config.get("metrics", [])
        superset_metrics = []
        for m in raw_metrics:
            if isinstance(m, str):
                superset_metrics.append({
                    "expressionType": "SQL",
                    "sqlExpression": m,
                    "label": m
                })
            else:
                superset_metrics.append(m)
        
        # Helper to map datasource_id
        def _resolve_datasource_id(config_dict: dict) -> int:
            TABLE_MAP = {
                "fct_user_event_tracking": 1,
                "dim_laptops_obt": 2,
                "dim_sessions": 3,
            }
            # Look at data_scope, or just check metrics/filters strings
            data_scope = str(config_dict).lower()
            for table_name, ds_id in TABLE_MAP.items():
                if table_name in data_scope:
                    return ds_id
            return 1  # default
            
        chart_type = config.get("chart_type", "table")
        
        # QA: Validate và fix metrics trước khi đẩy vào Superset
        superset_metrics = _validate_and_fix_metrics(
            superset_metrics,
            config.get("groupby", []),
            chart_type
        )
        
        datasource_id = _resolve_datasource_id(section) # use section to look at data_scope
        datasource_str = f"{datasource_id}__table"

        base_params = {
            "datasource": datasource_str,
            "time_range": "No filter",
            "row_limit": 1000,
        }

        if chart_type == "big_number":
            params_dict = {**base_params,
                "viz_type": "big_number_total",
                "metric": superset_metrics[0] if superset_metrics else {"expressionType":"SQL","sqlExpression":"COUNT(*)","label":"count"},
                "number_format": "SMART_NUMBER",
            }
        elif chart_type == "pie":
            params_dict = {**base_params,
                "viz_type": "pie",
                "metric": superset_metrics[0] if superset_metrics else {"expressionType":"SQL","sqlExpression":"COUNT(*)","label":"count"},
                "groupby": config.get("groupby", []),
                "pie_label_type": "key_percent",
                "show_labels": True,
                "show_legend": True,
                "number_format": "SMART_NUMBER",
            }
        elif chart_type == "line":
            groupby_raw = config.get("groupby", [])
            x_axis_col = config.get("time_column", "event_date")
            filtered_groupby = [g for g in groupby_raw if g != x_axis_col]
            
            params_dict = {**base_params,
                "viz_type": "echarts_timeseries_line",
                "metrics": superset_metrics,
                "groupby": filtered_groupby,
                "x_axis": x_axis_col,
                "granularity_sqla": x_axis_col,
            }
        elif chart_type == "bar":
            groupby_raw = config.get("groupby", [])
            x_axis_col = config.get("time_column", groupby_raw[0] if groupby_raw else "")
            filtered_groupby = [g for g in groupby_raw if g != x_axis_col]
            
            params_dict = {**base_params,
                "viz_type": "echarts_timeseries_bar",
                "metrics": superset_metrics,
                "groupby": filtered_groupby,
                "x_axis": x_axis_col,
            }
        else:  # table
            params_dict = {**base_params,
                "viz_type": "table",
                "metrics": superset_metrics,
                "groupby": config.get("groupby", []),
                "all_columns": config.get("groupby", []) if not superset_metrics else [],
            }
            
        chart_payload = {
            "slice_name": config.get("chart_name", "Untitled Chart"),
            "viz_type": params_dict["viz_type"],
            "datasource_id": datasource_id,
            "datasource_type": "table",
            "params": json.dumps(params_dict)
        }
        
        try:
            chart_res = session.post(f"{SUPERSET_URL}/api/v1/chart/", json=chart_payload, timeout=10)
            if chart_res.status_code == 201:
                chart_mappings.append({"chart_id": chart_res.json().get("id"), "section": section})
        except Exception as e:
            print(f"Lỗi khi tạo chart {chart_payload['slice_name']}: {e}")
            
    # 2. Xây dựng Layout Grid (position_json)
    import json
    position_json = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"},
        "GRID_ID": {"children": [], "id": "GRID_ID", "parents": ["ROOT_ID"], "type": "GRID"}
    }
    
    rows = {}
    for mapping in chart_mappings:
        chart_id = mapping["chart_id"]
        sec = mapping["section"]
        
        row_num = sec.get("row", 1)
        col_span = sec.get("col_span", 3)
        width = min(int(col_span) * 4, 12) # Map 3-col span to 12-col Superset Grid
        
        row_id = f"ROW_{row_num}"
        if row_id not in rows:
            rows[row_id] = True
            position_json["GRID_ID"]["children"].append(row_id)
            position_json[row_id] = {
                "children": [],
                "id": row_id,
                "meta": {"background": "BACKGROUND_TRANSPARENT"},
                "parents": ["ROOT_ID", "GRID_ID"],
                "type": "ROW"
            }
            
        # Responsive height based on chart type
        chart_type = sec.get("chart_config", {}).get("chart_type", "table")
        if chart_type == "big_number":
            height = 13
        elif chart_type in ("line", "bar", "pie"):
            height = 38
        else:  # table
            height = 45
            
        chart_uuid = f"CHART_{chart_id}"
        position_json[row_id]["children"].append(chart_uuid)
        position_json[chart_uuid] = {
            "children": [],
            "id": chart_uuid,
            "meta": {"chartId": chart_id, "width": width, "height": height},
            "parents": ["ROOT_ID", "GRID_ID", row_id],
            "type": "CHART"
        }

    # 3. Tạo Dashboard Draft
    dash_payload = {
        "dashboard_title": dashboard_name,
        "published": False,
        "position_json": json.dumps(position_json)
    }
    
    try:
        dash_res = session.post(f"{SUPERSET_URL}/api/v1/dashboard/", json=dash_payload, timeout=10)
        if dash_res.status_code == 201:
            dash_id = dash_res.json().get("id")
            
            # Link charts to dashboard
            for mapping in chart_mappings:
                chart_id = mapping["chart_id"]
                try:
                    session.put(f"{SUPERSET_URL}/api/v1/chart/{chart_id}", json={"dashboards": [dash_id]}, timeout=10)
                except Exception as e:
                    print(f"Lỗi khi link chart {chart_id} với dashboard {dash_id}: {e}")
                    
            return f"{SUPERSET_URL}/superset/dashboard/{dash_id}/"
        else:
            return f"Error: Không thể tạo Dashboard. Chi tiết: {dash_res.text}"
    except Exception as e:
        return f"Error: Lỗi hệ thống khi tạo Dashboard: {e}"
