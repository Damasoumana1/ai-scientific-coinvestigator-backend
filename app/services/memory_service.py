"""
Service de Mémoire Sémantique - Persistance du savoir de l'investigateur via Qdrant
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.settings import settings
from app.core.logging import logger
from datetime import datetime
import uuid

class MemoryService:
    """
    Gère la mémoire à long terme de l'agent.
    Stocke les découvertes, préférences et conclusions passées.
    """
    
    COLLECTION_NAME = "user_semantic_memory"
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.VECTOR_DB_URL,
            api_key=settings.VECTOR_DB_API_KEY
        )
        self._ensure_collection()

    def _ensure_collection(self):
        """Crée la collection si elle n'existe pas"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)
            
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.COLLECTION_NAME}")
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=models.VectorParams(
                        size=1536, # Taille standard OpenAI embeddings (text-embedding-3-small)
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")

    async def save_memory(self, user_id: str, content: str, metadata: Dict[str, Any] = None):
        """Sauvegarde un fragment de savoir dans la mémoire sémantique"""
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        try:
            # 1. Générer embedding
            response = await openai_client.embeddings.create(
                input=content,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            
            # 2. Upsert dans Qdrant
            point_id = str(uuid.uuid4())
            payload = {
                "user_id": user_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            logger.info(f"Memory fragment saved for user {user_id}")
            return point_id
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return None

    async def search_memory(self, user_id: str, query: str, limit: int = 5) -> List[str]:
        """Recherche des souvenirs pertinents pour un sujet donné"""
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        try:
            # 1. Générer embedding de la requête
            response = await openai_client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            
            # 2. Rechercher dans Qdrant filtré par user_id
            search_result = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=limit
            )
            
            memories = [hit.payload["content"] for hit in search_result if hit.score > 0.7]
            return memories
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []

    async def consolidate_analysis(self, user_id: str, project_id: str, analysis_result: Any):
        """
        Génère un résumé des points clés d'une analyse et les stocke en mémoire.
        """
        # Note: On utilise K2 pour générer le résumé sémantique si nécessaire
        # Pour le hackathon, on peut extraire les recommandations stratégiques et les gaps clés
        
        summary_parts = []
        if hasattr(analysis_result, 'reasoning_summary') and analysis_result.reasoning_summary:
            summary_parts.append(analysis_result.reasoning_summary)
            
        if hasattr(analysis_result, 'strategic_recommendations') and analysis_result.strategic_recommendations:
            recs = ". ".join(analysis_result.strategic_recommendations)
            summary_parts.append(f"Strategic Findings: {recs}")
            
        if not summary_parts:
            return
            
        full_context = "\n".join(summary_parts)
        
        # On peut demander à K2 de "condenser" cela en savoir réutilisable
        # Mais pour aller vite, on stocke le bloc tel quel ou par petits morceaux
        await self.save_memory(
            user_id=user_id,
            content=full_context,
            metadata={
                "project_id": project_id,
                "type": "analysis_consolidation"
            }
        )
