"""
Services for the cognitive architecture.

Services provide raw capabilities - external systems, APIs, and models.
"""

from .llm import LLMService, LLMResult
from .embedding import EmbeddingService

__all__ = [
    "LLMService",
    "LLMResult", 
    "EmbeddingService",
]