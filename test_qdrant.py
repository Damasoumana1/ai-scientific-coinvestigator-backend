from qdrant_client import QdrantClient
import sys

try:
    client = QdrantClient(url="http://localhost:6333")
    collections = client.get_collections()
    print("QDRANT CONNECTION SUCCESSFUL!")
    print(f"Collections found: {len(collections.collections)}")
except Exception as e:
    print(f"QDRANT CONNECTION FAILED: {e}")
