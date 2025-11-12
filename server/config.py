"""
Centralized configuration management using Pydantic Settings.
All environment variables and application settings are defined here.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    PINECONE_API_KEY: str
    
    # Pinecone Configuration
    PINECONE_ENV: str = "us-east-1"
    PINECONE_INDEX_NAME: str
    
    # Model Configuration
    EMBEDDING_MODEL: str = "models/embedding-001"
    EMBEDDING_DIMENSION: int = 768
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # Application Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    
    class Config:
        # Look for .env in server directory
        env_file = str(Path(__file__).parent / ".env")
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()


# Singleton instance for easy import
settings = get_settings()

