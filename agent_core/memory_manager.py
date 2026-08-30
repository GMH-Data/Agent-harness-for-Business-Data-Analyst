import uuid
import json
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from agent_core.qdrant_manager import get_qdrant_client, get_gemini_embedding

MEMORY_COLLECTION = "conversation_memory"
CACHE_COLLECTION = "validated_reports"
SIMILARITY_THRESHOLD = 0.95

# --- CONVERSATION MEMORY (LONG-TERM CACHE) ---

def save_turn_to_memory(task_id: str, subtask: str, step_index: int, user_motivation: str, turn_text: str):
    """Nhúng và đẩy bước vừa thực hiện lên Qdrant kèm Tags."""
    client = get_qdrant_client()
    vector = get_gemini_embedding(turn_text)
    
    client.upsert(
        collection_name=MEMORY_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "task_id": task_id,
                    "subtask": subtask,
                    "step_index": step_index,
                    "user_motivation": user_motivation,
                    "content": turn_text
                }
            )
        ]
    )

def recall_memory(task_id: str, subtask: str, query: str, limit: int = 5) -> list[dict]:
    """Tìm lại lịch sử cũ, có LỌC theo task_id & subtask và SẮP XẾP theo step_index."""
    client = get_qdrant_client()
    query_vector = get_gemini_embedding(query)
    
    results = client.query_points(
        collection_name=MEMORY_COLLECTION,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(key="task_id", match=MatchValue(value=task_id)),
                FieldCondition(key="subtask", match=MatchValue(value=subtask))
            ]
        ),
        limit=limit
    ).points
    
    # Trích xuất payload và sắp xếp lại theo step_index để đúng trình tự thời gian
    memories = [res.payload for res in results]
    memories.sort(key=lambda x: x.get("step_index", 0))
    return memories

# --- SEMANTIC CACHE (VALIDATED REPORTS) ---

def check_semantic_cache(user_question: str) -> dict | None:
    """Tìm kiếm câu hỏi tương tự trong Cache."""
    client = get_qdrant_client()
    query_vector = get_gemini_embedding(user_question)
    
    results = client.query_points(
        collection_name=CACHE_COLLECTION,
        query=query_vector,
        limit=1,
        score_threshold=SIMILARITY_THRESHOLD
    ).points
    
    if results:
        # Nếu có câu hỏi tương tự, trả về báo cáo cũ
        return results[0].payload
    return None

def save_to_semantic_cache(user_question: str, sql_query: str, report_data: dict):
    """Lưu báo cáo đã được người dùng duyệt vào Cache."""
    client = get_qdrant_client()
    vector = get_gemini_embedding(user_question)
    
    client.upsert(
        collection_name=CACHE_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "original_question": user_question,
                    "sql_query": sql_query,
                    "report_data": json.dumps(report_data, ensure_ascii=False)
                }
            )
        ]
    )
