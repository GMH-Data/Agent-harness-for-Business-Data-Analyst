from mcp.server.fastmcp import FastMCP
import json

# Khởi tạo MCP Server
mcp = FastMCP("RAG_Schema_Server")

# Dummy Data (Thực tế sẽ kết nối với Vector DB hoặc file JSON lớn)
DATABASE_SCHEMA = {
    "dim_users": {
        "description": "Bảng thông tin khách hàng, nhân khẩu học và phân loại khách hàng",
        "ddl": "CREATE TABLE dim_users (user_id STRING, user_name STRING, segment STRING, signup_date DATE);"
    },
    "fct_transactions": {
        "description": "Bảng dữ liệu giao dịch, doanh thu, đơn hàng",
        "ddl": "CREATE TABLE fct_transactions (transaction_id STRING, user_id STRING, amount FLOAT64, transaction_date DATE);"
    },
    "dim_products": {
        "description": "Bảng thông tin sản phẩm, danh mục hàng hóa",
        "ddl": "CREATE TABLE dim_products (product_id STRING, product_name STRING, category STRING, price FLOAT64);"
    }
}

@mcp.tool()
def search_tables(query: str) -> str:
    """
    Tìm kiếm các bảng trong cơ sở dữ liệu có liên quan đến câu hỏi (query).
    
    Args:
        query: Câu hỏi hoặc từ khóa cần tìm (VD: 'doanh thu theo khách hàng')
    """
    # Logic Dummy: Trong thực tế đây sẽ là hàm gọi Vector Search (VD: ChromaDB/Pinecone)
    # Tạm thời trả về 2 bảng mẫu nếu query có liên quan đến doanh thu / khách hàng
    relevant_tables = []
    query_lower = query.lower()
    
    if "doanh thu" in query_lower or "khách hàng" in query_lower:
        relevant_tables.append({"table_name": "dim_users", "description": DATABASE_SCHEMA["dim_users"]["description"]})
        relevant_tables.append({"table_name": "fct_transactions", "description": DATABASE_SCHEMA["fct_transactions"]["description"]})
        
    return json.dumps({"relevant_tables": relevant_tables}, ensure_ascii=False)

@mcp.tool()
def get_table_schema(table_names: list[str]) -> str:
    """
    Lấy chi tiết cấu trúc (DDL) của danh sách các bảng.
    
    Args:
        table_names: Danh sách tên bảng cần lấy (VD: ['dim_users', 'fct_transactions'])
    """
    schemas = []
    for table in table_names:
        if table in DATABASE_SCHEMA:
            schemas.append({
                "table_name": table,
                "ddl": DATABASE_SCHEMA[table]["ddl"]
            })
    return json.dumps({"schemas": schemas}, ensure_ascii=False)

if __name__ == "__main__":
    # Chạy MCP Server qua stdio
    mcp.run()
