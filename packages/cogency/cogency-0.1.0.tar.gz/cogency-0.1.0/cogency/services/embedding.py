"""
Embedding service abstraction.

Provides a unified interface for embedding operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..core.base import BaseService


@dataclass
class EmbeddingResult:
    """Result from an embedding operation."""
    
    embeddings: List[float]
    success: bool = True
    dimensions: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.dimensions is None and self.embeddings:
            self.dimensions = len(self.embeddings)


class EmbeddingService(BaseService, ABC):
    """
    Abstract base class for embedding services.
    
    Provides a unified interface for different embedding providers
    while maintaining provider-specific optimizations.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
    
    @abstractmethod
    async def embed(self, text: str, **kwargs) -> EmbeddingResult:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str], **kwargs) -> List[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        pass
    
    @abstractmethod
    async def similarity(self, text1: str, text2: str, **kwargs) -> float:
        """Calculate similarity between two texts."""
        pass
    
    @abstractmethod
    async def similarity_batch(
        self, 
        query_text: str, 
        texts: List[str], 
        **kwargs
    ) -> List[float]:
        """Calculate similarity between query and multiple texts."""
        pass
    
    @abstractmethod
    def get_dimensions(self) -> int:
        """Get the dimensionality of embeddings."""
        pass
    
    async def health_check(self) -> bool:
        """Check if the embedding service is healthy."""
        try:
            result = await self.embed("Test text")
            return result.success and len(result.embeddings) > 0
        except Exception:
            return False