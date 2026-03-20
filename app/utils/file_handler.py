"""
Utilitaires fichiers
"""
import os
from typing import Optional
from app.core.settings import settings


class FileHandler:
    """Gestion des fichiers"""
    
    @staticmethod
    def ensure_upload_dir():
        """Crée le répertoire d'upload s'il n'existe pas"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    @staticmethod
    def save_uploaded_file(file_content: bytes, filename: str) -> str:
        """Sauvegarde un fichier uploadé"""
        FileHandler.ensure_upload_dir()
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Supprime un fichier"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
