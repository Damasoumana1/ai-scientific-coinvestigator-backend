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
    
    COLLECTION_NAME = "user_semantic_memory_v2"
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.VECTOR_DB_URL,
            api_key=settings.VECTOR_DB_API_KEY
        )
        # On utilise FastEmbed pour des embeddings locaux et gratuits
        self.client.set_model("BAAI/bge-small-en-v1.5")
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
                    vectors_config={
                        "fast-bge-small-en-v1.5": models.VectorParams(
                            size=384,
                            distance=models.Distance.COSINE
                        )
                    }
                )
            else:
                # Si elle existe déjà mais avec le mauvais schéma (vecteur anonyme), 
                # Qdrant renverra l'erreur qu'on a vue. 
                # On pourrait la supprimer/recréer ici si on veut être radical.
                pass
            
            # Vérifier/Créer l'index user_id séparément pour être sûr
            try:
                self.client.create_payload_index(
                    collection_name=self.COLLECTION_NAME,
                    field_name="user_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                logger.info(f"Payload index ensured for 'user_id' in {self.COLLECTION_NAME}")
            except Exception:
                # L'index existe probablement déjà
                pass
                
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection or index: {e}")

    async def save_memory(self, user_id: str, content: str, metadata: Dict[str, Any] = None):
        """Sauvegarde un fragment de savoir dans la mémoire sémantique"""
        try:
            # 1. Upsert dans Qdrant avec embedding local automatique
            point_id = str(uuid.uuid4())
            payload = {
                "user_id": user_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # self.client.add gère l'embedding automatiquement grâce à set_model
            self.client.add(
                collection_name=self.COLLECTION_NAME,
                documents=[content],
                metadata=[payload],
                ids=[point_id]
            )
            
            logger.info(f"Memory fragment saved for user {user_id} via Local Embeddings")
            return point_id
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return None

    async def search_memory(self, user_id: str, query: str, limit: int = 5) -> List[str]:
        """Recherche des souvenirs pertinents pour un sujet donné"""
        try:
            # Recherche dans Qdrant avec embedding local automatique de la query
            search_result = self.client.query(
                collection_name=self.COLLECTION_NAME,
                query_text=query,
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
            
            memories = [hit.metadata["content"] for hit in search_result if hit.score > 0.6]
            return memories
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
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
