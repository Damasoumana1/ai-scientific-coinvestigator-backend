"""
Text cleaning utilities
"""
import re
import string


class TextCleaner:
    """Nettoyage de texte"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Nettoie le texte: suprime espaces doubles, caractères spéciaux"""
        # Supprime espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprime caractères de contrôle
        text = ''.join(ch for ch in text if ch.isprintable())
        
        # Trim
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_special_characters(text: str, keep_dots: bool = True) -> str:
        """Supprime caractères spéciaux"""
        if keep_dots:
            text = re.sub(r'[^\w\s\.\-,:]', '', text)
        else:
            text = re.sub(r'[^\w\s\-,:]', '', text)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalise les espaces"""
        return ' '.join(text.split())
