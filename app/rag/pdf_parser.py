"""
PDF Parser and Text Extraction
"""
import pypdf
import logging
import os
from typing import List, Tuple


class PDFParser:
    """Parser pour extraction de texte depuis PDF"""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extrait tout le texte d'un PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            raise ValueError(f"Erreur lors de l'extraction PDF: {str(e)}")
        return text
    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extrait métadonnées du PDF"""
        metadata = {}
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        "pages": len(pdf_reader.pages)
                    }
        except Exception as e:
            # It's better to log the error than to silently pass.
            logging.warning(f"Could not extract metadata from {file_path}: {str(e)}")
        return metadata
        return metadata
