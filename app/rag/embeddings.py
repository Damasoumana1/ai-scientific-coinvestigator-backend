"""
Embedding generation
"""
from typing import List
import numpy as np


class EmbeddingGenerator:
    """Générateur d'embeddings pour RAG"""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de textes
        """
        if self.provider == "openai":
            return await self._generate_openai_embeddings(texts)
        else:
            raise ValueError(f"Provider {self.provider} not supported")
    
    async def _generate_openai_embeddings(self, texts: List[str]):
        """Génère embeddings via OpenAI API"""
        try:
            import openai
            from app.core.settings import settings
            
            embeddings = []
            for text in texts:
                response = await openai.Embedding.acreate(
                    input=text,
                    model=settings.EMBEDDINGS_MODEL,
                    api_key=settings.OPENAI_API_KEY
                )
                embeddings.append(response['data'][0]['embedding'])
            
            return embeddings
        except Exception as e:
            raise ValueError(f"Error generating embeddings: {str(e)}")
