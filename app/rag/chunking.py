"""
Text chunking strategies for RAG
"""
from typing import List


class TextChunker:
    """Chunking de texte pour RAG"""
    
    @staticmethod
    def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Divise le texte en chunks avec chevauchement
        """
        chunks = []
        sentences = text.split('. ')
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip() + "."
            
            if len(current_chunk) + len(sentence) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                # Start new chunk with overlap
                current_chunk = chunks[-1][-overlap:] if chunks else ""
                current_chunk += sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    @staticmethod
    def chunk_by_section(text: str, section_markers: List[str] = None) -> dict:
        """
        Divise le texte par sections (abstract, methodology, results, etc.)
        """
        if section_markers is None:
            section_markers = [
                "abstract", "introduction", "methodology", "methods",
                "results", "discussion", "conclusion", "references"
            ]
        
        sections = {}
        current_section = "introduction"
        current_text = ""
        
        for line in text.split('\n'):
            line_lower = line.lower()
            found_marker = False
            
            for marker in section_markers:
                if marker in line_lower:
                    if current_section and current_text:
                        sections[current_section] = current_text
                    current_section = marker
                    current_text = line + "\n"
                    found_marker = True
                    break
            
            if not found_marker:
                current_text += line + "\n"
        
        if current_section and current_text:
            sections[current_section] = current_text
        
        return sections
