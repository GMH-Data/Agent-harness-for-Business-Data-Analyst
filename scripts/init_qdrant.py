import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models

def init_db():
    print("Connecting to Qdrant...")
    client = QdrantClient(host="localhost", port=6333)
    
    collections_to_create = ["schema_metadata", "analysis_memory"]
    
    for col in collections_to_create:
        print(f"Checking collection: {col}...")
        try:
            client.get_collection(collection_name=col)
            print(f"Collection {col} already exists. Skipping creation.")
        except Exception:
            print(f"Creating collection {col}...")
            client.create_collection(
                collection_name=col,
                vectors_config=models.VectorParams(
                    size=768,  # Kích thước vector chuẩn cho google text-embedding-004
                    distance=models.Distance.COSINE
                )
            )
            print(f"Successfully created collection: {col}")

if __name__ == "__main__":
    init_db()
