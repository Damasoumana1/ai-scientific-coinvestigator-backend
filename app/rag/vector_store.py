"""
Vector Store (Qdrant integration)
"""
from typing import List, Optional


class VectorStore:
    """Interface avec Qdrant pour stockage de vecteurs"""
    
    def __init__(self, url: str = None, api_key: str = None):
        from app.core.settings import settings
        self.url = url or settings.VECTOR_DB_URL
        self.api_key = api_key or settings.VECTOR_DB_API_KEY
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Cannot connect to Qdrant: {str(e)}")
    
    async def add_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[dict]
    ):
        """Ajoute des vecteurs à une collection"""
        try:
            from qdrant_client.models import PointStruct
            
            points = [
                PointStruct(
                    id=i,
                    vector=vector,
                    payload=payload
                )
                for i, (vector, payload) in enumerate(zip(vectors, payloads))
            ]
            
            await self.client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            raise ValueError(f"Error adding vectors: {str(e)}")
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5
    ) -> List[dict]:
        """Recherche les vecteurs similaires"""
        try:
            results = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return results
        except Exception as e:
            raise ValueError(f"Error searching vectors: {str(e)}")
