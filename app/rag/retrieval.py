"""
RAG Retrieval système
"""
from typing import List


class RAGRetriever:
    """Système de retrieval RAG complet"""
    
    def __init__(self, vector_store, embedding_generator):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    async def retrieve_relevant_chunks(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Récupère les chunks les plus pertinents
        """
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embeddings([query])
        
        # Search in vector store
        results = await self.vector_store.search(
            collection_name=collection_name,
            query_vector=query_embedding[0],
            limit=top_k
        )
        
        # Extract text from results
        relevant_chunks = [result.payload.get("text", "") for result in results]
        
        return relevant_chunks
