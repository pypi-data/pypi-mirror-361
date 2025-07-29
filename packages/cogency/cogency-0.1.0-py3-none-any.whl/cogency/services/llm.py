"""
LLM service abstraction.

Provides a unified interface for language model operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..core.base import BaseService


@dataclass
class LLMResult:
    """Result from an LLM operation."""
    
    content: str
    success: bool = True
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMService(BaseService, ABC):
    """
    Abstract base class for LLM services.
    
    Provides a unified interface for different LLM providers
    while maintaining provider-specific optimizations.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResult:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def analyze(
        self, 
        content: str, 
        focus: str = "general",
        **kwargs
    ) -> LLMResult:
        """Analyze content with a specific focus."""
        pass
    
    @abstractmethod
    async def extract(
        self, 
        content: str, 
        target: str,
        **kwargs
    ) -> LLMResult:
        """Extract specific information from content."""
        pass
    
    @abstractmethod
    async def classify(
        self, 
        content: str, 
        categories: List[str],
        **kwargs
    ) -> LLMResult:
        """Classify content into categories."""
        pass
    
    @abstractmethod
    async def evaluate(
        self, 
        content: str, 
        criteria: List[str],
        **kwargs
    ) -> LLMResult:
        """Evaluate content against criteria."""
        pass
    
    @abstractmethod
    async def synthesize(
        self, 
        sources: List[str], 
        focus: str = "comprehensive",
        **kwargs
    ) -> LLMResult:
        """Synthesize information from multiple sources."""
        pass
    
    @abstractmethod
    async def summarize(
        self, 
        content: str, 
        style: str = "concise",
        **kwargs
    ) -> LLMResult:
        """Summarize content in a specific style."""
        pass
    
    async def health_check(self) -> bool:
        """Check if the LLM service is healthy."""
        try:
            result = await self.generate("Test prompt", max_tokens=5)
            return result.success
        except Exception:
            return False