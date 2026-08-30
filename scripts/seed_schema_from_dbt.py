import os
import sys
import yaml
from qdrant_client import QdrantClient
from qdrant_client.http import models
from google import genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Thiếu biến môi trường GEMINI_API_KEY.")
    return genai.Client(api_key=api_key)

def seed_qdrant_from_dbt():
    print("Connecting to Qdrant...")
    q_client = QdrantClient(host="localhost", port=6333)
    
    col_name = "schema_metadata"
    try:
        q_client.get_collection(col_name)
    except Exception:
        print(f"Creating collection {col_name}...")
        q_client.create_collection(
            collection_name=col_name,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
        )

    # Đọc thông tin thực tế từ dbt models
    schema_path = os.path.join(os.path.dirname(__file__), "..", "dbt", "models", "gold", "schema.yml")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Không tìm thấy file: {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        dbt_schema = yaml.safe_load(f)

    g_client = get_gemini_client()
    points = []
    point_id = 1

    print("Generating embeddings from dbt schema.yml...")
    for model in dbt_schema.get("models", []):
        table_name = model["name"]
        table_desc = model.get("description", "")
        
        # Nhúng mô tả cấp độ bảng
        text_table = f"Table: {table_name}. Description: {table_desc}"
        try:
            embed_resp = g_client.models.embed_content(model="gemini-embedding-001", contents=text_table)
            vec = embed_resp.embeddings[0].values[:768]
        except Exception:
            vec = [0.1] * 768
            
        points.append(models.PointStruct(
            id=point_id,
            vector=vec,
            payload={
                "table_name": table_name,
                "description": table_desc,
                "type": "table"
            }
        ))
        point_id += 1

        # Nhúng mô tả cấp độ cột
        for col in model.get("columns", []):
            col_name_str = col["name"]
            col_desc = col.get("description", "")
            
            text_col = f"Table: {table_name}, Column: {col_name_str}. Description: {col_desc}"
            try:
                embed_resp = g_client.models.embed_content(model="gemini-embedding-001", contents=text_col)
                vec = embed_resp.embeddings[0].values[:768]
            except Exception:
                vec = [0.1] * 768
                
            points.append(models.PointStruct(
                id=point_id,
                vector=vec,
                payload={
                    "table_name": table_name,
                    "column_name": col_name_str,
                    "description": col_desc,
                    "type": "column"
                }
            ))
            point_id += 1

    q_client.upsert(collection_name=col_name, points=points)
    print(f"Successfully seeded {len(points)} records into {col_name} based on ACTUAL dbt schema!")

if __name__ == "__main__":
    seed_qdrant_from_dbt()
