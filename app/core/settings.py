"""
Core Settings & Configuration
"""
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Configuration de l'application"""

    # API
    API_TITLE: str = "AI Scientific Co-Investigator"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Advanced AI system for multi-document scientific analysis and experimental protocol design"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database — REQUIRED: must be set in .env
    DATABASE_URL: str = "postgresql://user:CHANGE_THIS_PASSWORD@localhost:5432/scoinvestigator"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    DB_ECHO: bool = False

    # Security — REQUIRED: must be set in .env
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_32_CHARS_MINIMUM"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Frontend URL (Used for OAuth redirects)
    FRONTEND_URL: str = "https://ai-scientific-coinvestigator-ui.vercel.app"

    # CORS — array or comma-separated list of allowed origins
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://ai-scientific-coinvestigator-ui.vercel.app"]
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # OpenAI/LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo"

    # K2 Think (Unique AI Engine for Hackathon)
    K2_THINK_API_KEY: Optional[str] = None
    K2_THINK_API_URL: str = "https://api.k2think.ai/v1"

    # RAG
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"
    VECTOR_DB_URL: str = "http://localhost:6333"  # Qdrant
    VECTOR_DB_API_KEY: Optional[str] = None
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # File Upload
    UPLOAD_DIR: str = "./uploaded_files"
    MAX_FILE_SIZE_MB: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    # If not set, the app will try to construct it from the request URL
    GOOGLE_REDIRECT_URI: Optional[str] = None

    @field_validator(
        "GOOGLE_CLIENT_ID", 
        "GOOGLE_CLIENT_SECRET", 
        "GOOGLE_REDIRECT_URI",
        "OPENAI_API_KEY",
        "K2_THINK_API_KEY",
        "SECRET_KEY",
        "DATABASE_URL",
        mode="before"
    )
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

