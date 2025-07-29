"""
Content analysis tool.

Provides smart analysis capabilities with caching and validation.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import hashlib
import logging

from ..core.base import BaseTool
from ..services.llm import LLMService
from ..services.embedding import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result from content analysis."""
    
    insights: List[str]
    themes: List[str]
    embeddings: Optional[List[float]] = None
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentAnalysisTool(BaseTool):
    """
    Smart content analysis tool with caching and validation.
    
    Orchestrates LLM and embedding services to provide comprehensive
    content analysis with performance optimizations.
    """
    
    def __init__(self, llm_service: LLMService, embedding_service: EmbeddingService):
        super().__init__("content_analysis")
        self.llm = llm_service
        self.embeddings = embedding_service
        self._cache: Dict[str, AnalysisResult] = {}
        self._max_cache_size = 100
    
    async def analyze_content(self, content: str, intent: str = "general") -> AnalysisResult:
        """
        Analyze content with caching and validation.
        
        Args:
            content: Text content to analyze
            intent: Analysis intent (general, technical, creative, etc.)
            
        Returns:
            AnalysisResult with insights, themes, and embeddings
        """
        # Input validation
        if not content or not content.strip():
            return AnalysisResult(
                insights=["No content provided"],
                themes=["empty"],
                confidence=0.0,
                metadata={"error": "empty_content"}
            )
        
        # Cache key
        cache_key = self._get_cache_key(content, intent)
        
        # Check cache
        if cache_key in self._cache:
            logger.debug(f"Cache hit for content analysis: {cache_key[:10]}...")
            return self._cache[cache_key]
        
        try:
            # Execute analysis and embedding in parallel
            analysis_task = asyncio.create_task(
                self.llm.analyze(content, focus=intent)
            )
            embedding_task = asyncio.create_task(
                self.embeddings.embed(content)
            )
            
            # Wait for both to complete
            analysis_result, embedding_result = await asyncio.gather(
                analysis_task, embedding_task, return_exceptions=True
            )
            
            # Handle analysis result
            if isinstance(analysis_result, Exception):
                logger.error(f"Analysis failed: {analysis_result}")
                insights = ["Analysis failed"]
                themes = ["error"]
                confidence = 0.0
            else:
                insights = self._extract_insights(analysis_result.content)
                themes = self._extract_themes(analysis_result.content)
                confidence = analysis_result.confidence
            
            # Handle embedding result
            if isinstance(embedding_result, Exception):
                logger.error(f"Embedding failed: {embedding_result}")
                embeddings = None
            else:
                embeddings = embedding_result.embeddings
            
            # Create result
            result = AnalysisResult(
                insights=insights,
                themes=themes,
                embeddings=embeddings,
                confidence=confidence,
                metadata={
                    "intent": intent,
                    "content_length": len(content),
                    "analysis_method": "parallel"
                }
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return AnalysisResult(
                insights=[f"Analysis error: {str(e)}"],
                themes=["error"],
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def quick_analyze(self, content: str, intent: str = "general") -> AnalysisResult:
        """Quick analysis without embeddings."""
        try:
            result = await self.llm.analyze(content, focus=intent)
            return AnalysisResult(
                insights=self._extract_insights(result.content),
                themes=self._extract_themes(result.content),
                confidence=result.confidence,
                metadata={"method": "quick", "intent": intent}
            )
        except Exception as e:
            logger.error(f"Quick analysis failed: {e}")
            return AnalysisResult(
                insights=[f"Quick analysis error: {str(e)}"],
                themes=["error"],
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def deep_analyze(self, content: str, intent: str = "general") -> AnalysisResult:
        """Deep analysis with multiple passes."""
        try:
            # First pass: general analysis
            general_result = await self.llm.analyze(content, focus="general")
            
            # Second pass: focused analysis
            focused_result = await self.llm.analyze(content, focus=intent)
            
            # Get embeddings
            embedding_result = await self.embeddings.embed(content)
            
            # Combine insights
            combined_insights = (
                self._extract_insights(general_result.content) +
                self._extract_insights(focused_result.content)
            )
            
            # Remove duplicates while preserving order
            unique_insights = []
            seen = set()
            for insight in combined_insights:
                if insight not in seen:
                    unique_insights.append(insight)
                    seen.add(insight)
            
            return AnalysisResult(
                insights=unique_insights,
                themes=self._extract_themes(general_result.content + focused_result.content),
                embeddings=embedding_result.embeddings,
                confidence=min(general_result.confidence, focused_result.confidence),
                metadata={"method": "deep", "intent": intent, "passes": 2}
            )
            
        except Exception as e:
            logger.error(f"Deep analysis failed: {e}")
            return AnalysisResult(
                insights=[f"Deep analysis error: {str(e)}"],
                themes=["error"],
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _get_cache_key(self, content: str, intent: str) -> str:
        """Generate cache key for content and intent."""
        combined = f"{content}|{intent}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _cache_result(self, cache_key: str, result: AnalysisResult) -> None:
        """Cache analysis result with size limit."""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[cache_key] = result
    
    def _extract_insights(self, content: str) -> List[str]:
        """Extract insights from LLM response."""
        # Simple extraction - can be enhanced with structured prompts
        lines = content.strip().split('\n')
        insights = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                insights.append(line)
        
        return insights[:5]  # Limit to top 5 insights
    
    def _extract_themes(self, content: str) -> List[str]:
        """Extract themes from LLM response."""
        # Simple theme extraction - can be enhanced
        words = content.lower().split()
        
        # Simple frequency-based theme extraction
        word_count = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_count[word] = word_count.get(word, 0) + 1
        
        # Get top themes
        themes = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in themes[:3]]
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
        logger.info("Content analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self._max_cache_size,
            "cache_keys": list(self._cache.keys())
        }