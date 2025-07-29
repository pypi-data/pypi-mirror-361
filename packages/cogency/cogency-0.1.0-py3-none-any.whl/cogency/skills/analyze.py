"""
Analyze skill - understanding structure, meaning, and context of content.
"""

from typing import Dict, Any, Optional
import logging

from ..core.result import SkillResult, SkillStatus, SkillError
from ..core.context import SkillContext
from ..core.base import skill as skill_base
from ..tools.content_analysis import ContentAnalysisTool
from ..registry import get_tool
from .registry import skill

logger = logging.getLogger(__name__)


@skill_base
@skill(
    name="analyze",
    description="Understand structure, meaning, and context of content",
    category="cognitive",
    version="1.0.0",
    author="cogency",
    aliases=["understand", "comprehend"],
    tags=["content", "analysis", "insights", "themes"]
)
async def analyze(
    context: SkillContext, 
    content: str,
    focus: str = "general",
    deep_analysis: Optional[bool] = None
) -> SkillResult[Dict[str, Any]]:
    """
    Understand structure, meaning, and context of content.
    
    This is a core cognitive skill that analyzes content to extract
    insights, themes, and semantic understanding.
    
    Args:
        context: Skill execution context
        content: Content to analyze
        focus: Analysis focus (general, technical, creative, etc.)
        deep_analysis: Force deep analysis (overrides context setting)
        
    Returns:
        SkillResult with analysis data including insights and themes
    """
    # Input validation
    if not content or not content.strip():
        return SkillResult(
            status=SkillStatus.FAILED,
            confidence=0.0,
            errors=[SkillError(
                error_type="validation_error",
                message="Content is empty or whitespace only",
                recoverable=False
            )]
        )
    
    try:
        # Get analysis tool
        analysis_tool = get_tool(ContentAnalysisTool)
        
        # Cognitive decision: How should I analyze this?
        requires_deep = deep_analysis if deep_analysis is not None else context.requires_deep_analysis
        
        if requires_deep:
            logger.info("Performing deep analysis")
            result = await analysis_tool.deep_analyze(content, focus)
        else:
            logger.info("Performing quick analysis")
            result = await analysis_tool.quick_analyze(content, focus)
        
        # Convert tool result to skill result
        analysis_data = {
            "insights": result.insights,
            "themes": result.themes,
            "embeddings": result.embeddings,
            "focus": focus,
            "method": result.metadata.get("method", "unknown")
        }
        
        return SkillResult(
            data=analysis_data,
            status=SkillStatus.COMPLETED,
            confidence=result.confidence,
            metadata={
                "content_length": len(content),
                "focus": focus,
                "deep_analysis": requires_deep,
                "tool_metadata": result.metadata
            }
        )
        
    except Exception as e:
        logger.error(f"Analysis skill failed: {e}")
        
        # Attempt graceful degradation
        try:
            # Try basic pattern-based analysis
            basic_analysis = _basic_content_analysis(content)
            
            return SkillResult(
                data=basic_analysis,
                status=SkillStatus.COMPLETED,
                confidence=0.3,  # Low confidence for fallback
                metadata={"fallback": True, "original_error": str(e)},
                errors=[SkillError(
                    error_type="tool_failure",
                    message=f"Primary analysis failed, used fallback: {str(e)}",
                    recoverable=True
                )]
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback analysis also failed: {fallback_error}")
            
            return SkillResult(
                status=SkillStatus.FAILED,
                confidence=0.0,
                errors=[
                    SkillError(
                        error_type="skill_failure",
                        message=f"Both primary and fallback analysis failed: {str(e)}",
                        recoverable=True
                    )
                ]
            )


def _basic_content_analysis(content: str) -> Dict[str, Any]:
    """
    Basic content analysis fallback.
    
    Provides simple pattern-based analysis when sophisticated tools fail.
    """
    words = content.lower().split()
    
    # Basic statistics
    word_count = len(words)
    unique_words = len(set(words))
    
    # Simple theme extraction (most common words)
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
    themes = [theme[0] for theme in top_themes]
    
    # Basic insights
    insights = [
        f"Content contains {word_count} words with {unique_words} unique words",
        f"Vocabulary diversity: {unique_words/word_count:.2f}" if word_count > 0 else "Empty content",
        f"Most common themes: {', '.join(themes)}" if themes else "No clear themes identified"
    ]
    
    return {
        "insights": insights,
        "themes": themes,
        "embeddings": None,
        "focus": "basic",
        "method": "fallback"
    }