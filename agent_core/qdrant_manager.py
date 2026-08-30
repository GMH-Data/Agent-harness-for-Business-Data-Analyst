import os
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv

load_dotenv()

# Khởi tạo Gemini Client (sẽ tự động lấy GEMINI_API_KEY từ biến môi trường)
gemini_client = genai.Client()

def get_qdrant_client() -> QdrantClient:
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")
    if not url or not api_key:
        raise ValueError("Thiếu biến môi trường QDRANT_URL hoặc QDRANT_API_KEY")
    return QdrantClient(url=url, api_key=api_key)

def get_gemini_embedding(text: str) -> list[float]:
    """Sử dụng Gemini để tạo Vector embedding cho đoạn văn bản."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    return response.embeddings[0].values

def init_collections(vector_size: int = 3072):
    """Khởi tạo 3 bộ nhớ: Schema RAG, Semantic Cache và Conversation Memory."""
    client = get_qdrant_client()
    
    # 1. Bảng Schema
    if not client.collection_exists("schema_metadata"):
        client.create_collection(
            collection_name="schema_metadata",
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print("Đã tạo collection mới: schema_metadata")
    else:
        print("Collection schema_metadata đã tồn tại.")
        
    # 2. Bảng Semantic Cache
    if not client.collection_exists("validated_reports"):
        client.create_collection(
            collection_name="validated_reports",
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print("Đã tạo collection mới: validated_reports")
    else:
        print("Collection validated_reports đã tồn tại.")
        
    # 3. Bảng Conversation Memory (Với index cho Metadata)
    if not client.collection_exists("conversation_memory"):
        client.create_collection(
            collection_name="conversation_memory",
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        # Tạo Index cho các Metadata để truy vấn cực nhanh
        client.create_payload_index("conversation_memory", field_name="task_id", field_schema="keyword")
        client.create_payload_index("conversation_memory", field_name="subtask", field_schema="keyword")
        client.create_payload_index("conversation_memory", field_name="step_index", field_schema="integer")
        print("Đã tạo collection mới và indexes: conversation_memory")
    else:
        print("Collection conversation_memory đã tồn tại.")

def retrieve_schema(query: str, limit: int = 3) -> str:
    """Truy xuất cấu trúc bảng từ schema_metadata dựa trên query."""
    try:
        client = get_qdrant_client()
        query_vector = get_gemini_embedding(query)
        results = client.query_points(
            collection_name="schema_metadata",
            query=query_vector,
            limit=limit
        ).points
        schema_contexts = []
        for res in results:
            schema_contexts.append(res.payload.get("schema_json", ""))
        return "\n\n".join(schema_contexts)
    except Exception as e:
        print(f"Lỗi khi retrieve schema: {e}")
        return ""

def retrieve_dashboard_template(query: str, limit: int = 2) -> str:
    """Tìm kiếm Layout Template từ validated_reports có chứa dashboard_blueprint."""
    try:
        client = get_qdrant_client()
        query_vector = get_gemini_embedding(query)
        results = client.query_points(
            collection_name="validated_reports",
            query=query_vector,
            limit=limit
        ).points
        templates = []
        for res in results:
            payload = res.payload
            if "dashboard_blueprint" in str(payload):
                templates.append(payload.get("report_data", ""))
        return "\n\n".join(templates) if templates else ""
    except Exception as e:
        print(f"Lỗi khi retrieve dashboard template: {e}")
        return ""


def save_dashboard_template(dashboard_name: str, blueprint: dict, user_question: str):
    """Lưu Blueprint đã được duyệt thành Template mới trong validated_reports."""
    import uuid
    import json
    from qdrant_client.http.models import PointStruct
    try:
        client = get_qdrant_client()
        vector = get_gemini_embedding(user_question)
        client.upsert(
            collection_name="validated_reports",
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "original_question": user_question,
                        "type": "dashboard_template",
                        "dashboard_name": dashboard_name,
                        "dashboard_blueprint": json.dumps(blueprint, ensure_ascii=False),
                        "report_data": json.dumps(blueprint, ensure_ascii=False)
                    }
                )
            ]
        )
        print(f"Đã lưu Dashboard Template: {dashboard_name}")
    except Exception as e:
        print(f"Lỗi khi lưu dashboard template: {e}")

if __name__ == "__main__":
    init_collections()
    print("Test embedding (Hello World):")
    emb = get_gemini_embedding("Hello World")
    print(f"Embedding length: {len(emb)}")
    print(f"First 5 dimensions: {emb[:5]}")
