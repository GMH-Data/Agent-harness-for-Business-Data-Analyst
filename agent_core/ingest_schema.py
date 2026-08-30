import os
import uuid
import yaml
import json
from pathlib import Path
from qdrant_client.http.models import PointStruct
from agent_core.qdrant_manager import get_qdrant_client, get_gemini_embedding, init_collections

COLLECTION_NAME = "schema_metadata"

def parse_dbt_schema_to_json(yml_path: str) -> list[dict]:
    """Phân tích file dbt schema.yml thành định dạng JSON có cấu trúc."""
    with open(yml_path, 'r', encoding='utf-8') as f:
        schema_data = yaml.safe_load(f)
        
    tables = []
    if not schema_data or 'models' not in schema_data:
        return tables
        
    for model in schema_data['models']:
        table_name = model.get('name', 'Unknown')
        table_desc = model.get('description', '')
        
        columns = []
        if 'columns' in model:
            for col in model['columns']:
                columns.append({
                    "name": col.get('name', ''),
                    "description": col.get('description', ''),
                    "type": col.get('data_type', 'unknown')
                })
                
        table_json_schema = {
            "table_name": table_name,
            "description": table_desc,
            "columns": columns,
            "relationships": [] 
        }
        
        search_text = f"Bảng {table_name}: {table_desc}"
        
        tables.append({
            "table_name": table_name,
            "search_text": search_text,
            "json_payload": table_json_schema
        })
        
    return tables

def ingest_schemas():
    """Đọc schema từ dbt và nạp lên Qdrant dưới dạng JSON."""
    project_root = Path(__file__).parent.parent
    dbt_gold_schema = os.path.join(project_root, "dbt", "models", "gold", "schema.yml")
    
    print("Đang đọc dbt schema và chuyển sang dạng JSON...")
    if not os.path.exists(dbt_gold_schema):
        print(f"Không tìm thấy file: {dbt_gold_schema}")
        return
        
    tables = parse_dbt_schema_to_json(dbt_gold_schema)
    
    if not tables:
        print("Không tìm thấy dữ liệu bảng nào!")
        return

    init_collections()
    client = get_qdrant_client()
    points = []
    
    for table in tables:
        print(f"Đang sinh Vector cho tóm tắt bảng: {table['table_name']}")
        vector = get_gemini_embedding(table['search_text'])
        
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "schema_json": json.dumps(table['json_payload'], ensure_ascii=False),
                    "source": "dbt_gold_layer"
                }
            )
        )
        
    print(f"Đang đẩy {len(points)} JSON schemas lên Qdrant Cloud...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print("Nạp JSON Schema Metadata thành công!")

if __name__ == "__main__":
    ingest_schemas()
