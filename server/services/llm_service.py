"""
Centralized LLM Service for ChatGroq operations.
Provides factory methods for creating LLM instances with different configurations.
"""

from functools import lru_cache
from langchain_groq import ChatGroq

from config import settings
from logger import logger


class LLMService:
    """Centralized service for LLM operations."""
    
    @staticmethod
    def get_llm(
        temperature: float = 0.1,
        streaming: bool = False,
        model: str = None
    ) -> ChatGroq:
        """
        Get a ChatGroq LLM instance.
        
        Args:
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            streaming: Enable streaming responses
            model: Model name (defaults to settings.LLM_MODEL)
        
        Returns:
            Configured ChatGroq instance
        """
        model_name = model or settings.LLM_MODEL
        logger.debug(f"Creating LLM instance: {model_name}, temp={temperature}, streaming={streaming}")
        
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming
        )
    
    @staticmethod
    def get_rag_llm() -> ChatGroq:
        """
        Get LLM configured for RAG (low temperature for accuracy).
        
        Returns:
            ChatGroq instance optimized for RAG
        """
        return LLMService.get_llm(temperature=0.1, streaming=False)
    
    @staticmethod
    def get_chat_llm() -> ChatGroq:
        """
        Get LLM configured for chat (moderate temperature for conversation).
        
        Returns:
            ChatGroq instance optimized for conversational chat
        """
        return LLMService.get_llm(temperature=0.5, streaming=True)


@lru_cache()
def get_llm_service() -> LLMService:
    """Get singleton LLM service instance."""
    return LLMService()

