import json
from typing import Dict, Any
from agent_core.state import AgentState


def assembler_node(state: AgentState) -> Dict[str, Any]:
    """
    Dashboard Assembler:
    1. Nhận toàn bộ dashboard_sections[] đã hoàn thành
    2. Tổng hợp thông tin từ Blueprint + Sections
    3. Tạo Draft Report mô tả Dashboard cho User duyệt
    4. Trong tương lai: Gọi Superset MCP để ráp Dashboard thực tế
    """
    blueprint = state.get("dashboard_blueprint", {})
    sections = state.get("dashboard_sections", []) or []
    dashboard_name = blueprint.get("dashboard_name", "Untitled Dashboard")
    storyline = blueprint.get("storyline", "")
    
    # Build Dashboard Summary Report
    report_parts = [
        f"# 📊 DASHBOARD: {dashboard_name}",
        f"\n## 🎯 Storyline",
        f"{storyline}",
        f"\n## 📋 Cấu trúc Dashboard ({len(sections)} sections)",
    ]
    
    for i, section in enumerate(sections):
        chart_config = section.get("chart_config", {})
        report_parts.append(
            f"\n### Section {i+1}: {section.get('section_id', '')}\n"
            f"- **Mục tiêu:** {section.get('section_goal', '')}\n"
            f"- **Loại biểu đồ:** {chart_config.get('chart_type', 'N/A')}\n"
            f"- **Tên:** {chart_config.get('chart_name', 'N/A')}\n"
            f"- **Metrics:** {', '.join(chart_config.get('metrics', []))}\n"
            f"- **Group by:** {', '.join(chart_config.get('groupby', []))}"
        )
    
    report_parts.append(f"\n---\n*Dashboard này đã được tạo bản nháp trên Superset. Vui lòng kiểm tra và public nếu hợp lệ.*")
    
    # Gọi Superset MCP để ráp Dashboard thực tế
    from agent_core.mcp.superset_mcp_tool import create_draft_dashboard
    preview_url = create_draft_dashboard(dashboard_name, sections)
    
    return {
        "draft_report": "\n".join(report_parts),
        "dashboard_preview_url": preview_url
    }
