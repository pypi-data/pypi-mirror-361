"""
Synthesize skill - combining information from multiple sources.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ..core.result import SkillResult, SkillStatus, SkillError
from ..core.context import SkillContext
from ..core.base import skill as skill_base
from ..services.llm import LLMService
from ..registry import get_service
from .registry import skill

logger = logging.getLogger(__name__)


@skill_base
@skill(
    name="synthesize",
    description="Combine information from multiple sources into coherent synthesis",
    category="cognitive",
    version="1.0.0",
    author="cogency",
    aliases=["combine", "merge", "integrate"],
    tags=["synthesis", "combination", "integration", "coherence"]
)
async def synthesize(
    context: SkillContext,
    sources: Union[List[str], List[Dict[str, Any]]],
    focus: str = "comprehensive",
    max_length: Optional[int] = None,
    style: str = "informative"
) -> SkillResult[Dict[str, Any]]:
    """
    Combine information from multiple sources into a cohesive synthesis.
    
    This cognitive skill takes multiple pieces of information and creates
    a unified, coherent understanding by finding connections and patterns.
    
    Args:
        context: Skill execution context
        sources: List of source content (strings or dicts with content)
        focus: Synthesis focus (comprehensive, summary, analysis, etc.)
        max_length: Optional maximum length for synthesis
        style: Synthesis style (informative, narrative, analytical, etc.)
        
    Returns:
        SkillResult with synthesized content and metadata
    """
    # Input validation
    if not sources:
        return SkillResult(
            status=SkillStatus.FAILED,
            confidence=0.0,
            errors=[SkillError(
                error_type="validation_error",
                message="No sources provided for synthesis",
                recoverable=False
            )]
        )
    
    if len(sources) < 2:
        return SkillResult(
            status=SkillStatus.FAILED,
            confidence=0.0,
            errors=[SkillError(
                error_type="validation_error",
                message="At least 2 sources required for synthesis",
                recoverable=False
            )]
        )
    
    try:
        # Get LLM service
        llm_service = get_service(LLMService)
        
        # Normalize sources to strings
        normalized_sources = _normalize_sources(sources)
        
        # Cognitive decision: What type of synthesis should I perform?
        if focus.lower() in ["summary", "brief", "concise"]:
            logger.info("Performing summary synthesis")
            result = await _summary_synthesis(llm_service, normalized_sources, style)
        elif focus.lower() in ["analysis", "analytical", "compare"]:
            logger.info("Performing analytical synthesis")
            result = await _analytical_synthesis(llm_service, normalized_sources, style)
        elif focus.lower() in ["narrative", "story", "flow"]:
            logger.info("Performing narrative synthesis")
            result = await _narrative_synthesis(llm_service, normalized_sources, style)
        else:
            logger.info("Performing comprehensive synthesis")
            result = await _comprehensive_synthesis(llm_service, normalized_sources, style)
        
        # Apply length constraints if specified
        if max_length and result.get("content"):
            result["content"] = _truncate_content(result["content"], max_length)
        
        synthesis_data = {
            "content": result.get("content", ""),
            "key_themes": result.get("themes", []),
            "source_count": len(normalized_sources),
            "synthesis_type": focus,
            "style": style,
            "connections": result.get("connections", [])
        }
        
        return SkillResult(
            data=synthesis_data,
            status=SkillStatus.COMPLETED,
            confidence=result.get("confidence", 0.8),
            metadata={
                "source_count": len(normalized_sources),
                "focus": focus,
                "style": style,
                "synthesis_method": result.get("method", "unknown"),
                "total_source_length": sum(len(s) for s in normalized_sources)
            }
        )
        
    except Exception as e:
        logger.error(f"Synthesis skill failed: {e}")
        
        # Attempt graceful degradation
        try:
            # Try basic text combination
            basic_synthesis = _basic_synthesis(sources, focus)
            
            return SkillResult(
                data=basic_synthesis,
                status=SkillStatus.COMPLETED,
                confidence=0.3,  # Low confidence for fallback
                metadata={"fallback": True, "original_error": str(e)},
                errors=[SkillError(
                    error_type="tool_failure",
                    message=f"Primary synthesis failed, used fallback: {str(e)}",
                    recoverable=True
                )]
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback synthesis also failed: {fallback_error}")
            
            return SkillResult(
                status=SkillStatus.FAILED,
                confidence=0.0,
                errors=[
                    SkillError(
                        error_type="skill_failure",
                        message=f"Both primary and fallback synthesis failed: {str(e)}",
                        recoverable=True
                    )
                ]
            )


def _normalize_sources(sources: Union[List[str], List[Dict[str, Any]]]) -> List[str]:
    """Normalize sources to strings."""
    normalized = []
    
    for source in sources:
        if isinstance(source, str):
            normalized.append(source)
        elif isinstance(source, dict):
            # Try to extract content from dict
            content = source.get("content", source.get("text", source.get("data", "")))
            if isinstance(content, str):
                normalized.append(content)
            else:
                normalized.append(str(content))
        else:
            normalized.append(str(source))
    
    return normalized


async def _comprehensive_synthesis(
    llm_service: LLMService, 
    sources: List[str], 
    style: str
) -> Dict[str, Any]:
    """Perform comprehensive synthesis."""
    # Combine all sources
    combined_content = "\n\n---\n\n".join(sources)
    
    result = await llm_service.synthesize(
        sources=sources,
        focus="comprehensive"
    )
    
    # Extract themes and connections
    themes = _extract_themes_from_synthesis(result.content)
    connections = _identify_connections(sources)
    
    return {
        "content": result.content,
        "themes": themes,
        "connections": connections,
        "method": "comprehensive",
        "confidence": result.confidence
    }


async def _summary_synthesis(
    llm_service: LLMService, 
    sources: List[str], 
    style: str
) -> Dict[str, Any]:
    """Perform summary synthesis."""
    result = await llm_service.synthesize(
        sources=sources,
        focus="summary"
    )
    
    themes = _extract_themes_from_synthesis(result.content)
    
    return {
        "content": result.content,
        "themes": themes,
        "connections": [],
        "method": "summary",
        "confidence": result.confidence
    }


async def _analytical_synthesis(
    llm_service: LLMService, 
    sources: List[str], 
    style: str
) -> Dict[str, Any]:
    """Perform analytical synthesis."""
    result = await llm_service.synthesize(
        sources=sources,
        focus="analysis"
    )
    
    themes = _extract_themes_from_synthesis(result.content)
    connections = _identify_connections(sources)
    
    return {
        "content": result.content,
        "themes": themes,
        "connections": connections,
        "method": "analytical",
        "confidence": result.confidence
    }


async def _narrative_synthesis(
    llm_service: LLMService, 
    sources: List[str], 
    style: str
) -> Dict[str, Any]:
    """Perform narrative synthesis."""
    result = await llm_service.synthesize(
        sources=sources,
        focus="narrative"
    )
    
    themes = _extract_themes_from_synthesis(result.content)
    
    return {
        "content": result.content,
        "themes": themes,
        "connections": [],
        "method": "narrative",
        "confidence": result.confidence
    }


def _extract_themes_from_synthesis(content: str) -> List[str]:
    """Extract themes from synthesized content."""
    # Simple theme extraction - can be enhanced
    words = content.lower().split()
    
    # Count word frequency
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top themes
    top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return [theme[0] for theme in top_themes]


def _identify_connections(sources: List[str]) -> List[str]:
    """Identify connections between sources."""
    connections = []
    
    # Simple connection identification
    for i, source1 in enumerate(sources):
        for j, source2 in enumerate(sources[i+1:], i+1):
            # Find common significant words
            words1 = set(word.lower() for word in source1.split() if len(word) > 4)
            words2 = set(word.lower() for word in source2.split() if len(word) > 4)
            
            common_words = words1 & words2
            if len(common_words) > 2:
                connections.append(f"Sources {i+1} and {j+1} share themes: {', '.join(list(common_words)[:3])}")
    
    return connections


def _basic_synthesis(sources: Union[List[str], List[Dict[str, Any]]], focus: str) -> Dict[str, Any]:
    """Basic synthesis fallback."""
    normalized_sources = _normalize_sources(sources)
    
    # Simple concatenation with separators
    combined = [f"\n\n--- Source {i+1} ---\n\n{source}" for i, source in enumerate(normalized_sources)]
    content = "\n".join(combined)
    
    # Basic theme extraction
    all_words = []
    for source in normalized_sources:
        all_words.extend(source.lower().split())
    
    word_freq = {}
    for word in all_words:
        if len(word) > 4:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
    themes = [theme[0] for theme in top_themes]
    
    return {
        "content": content,
        "key_themes": themes,
        "source_count": len(normalized_sources),
        "synthesis_type": focus,
        "style": "basic",
        "connections": []
    }


def _truncate_content(content: str, max_length: int) -> str:
    """Truncate content to maximum length."""
    if len(content) <= max_length:
        return content
    
    # Try to truncate at sentence boundary
    truncated = content[:max_length]
    last_sentence = truncated.rfind('.')
    
    if last_sentence > max_length * 0.8:  # If we can keep most of the content
        return truncated[:last_sentence + 1]
    else:
        return truncated + "..."