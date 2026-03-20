"""
Database Models for Paper Chunks (RAG)
"""
from sqlalchemy import Column, Integer, Text, ForeignKey, UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class PaperChunk(Base):
    """Chunk de texte d'un article (pour RAG)"""
    __tablename__ = "paper_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("research_papers.id"), nullable=False)
    chunk_index = Column(Integer)
    content = Column(Text)
    section = Column(Text)
    _metadata = Column("metadata", JSON)
    
    # Relationships
    paper = relationship("ResearchPaper", back_populates="chunks")
    
    def __repr__(self):
        return f"<PaperChunk {self.paper_id}_{self.chunk_index}>"
