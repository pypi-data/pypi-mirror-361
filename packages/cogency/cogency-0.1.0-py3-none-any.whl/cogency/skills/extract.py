"""
Extract skill - pulling specific information from content.
"""

from typing import Dict, Any, Optional, List
import logging

from ..core.result import SkillResult, SkillStatus, SkillError
from ..core.context import SkillContext
from ..core.base import skill as skill_base
from ..tools.content_extraction import ContentExtractionTool
from ..registry import get_tool
from .registry import skill

logger = logging.getLogger(__name__)


@skill_base
@skill(
    name="extract",
    description="Extract specific information from content",
    category="cognitive",
    version="1.0.0",
    author="cogency",
    aliases=["pull", "find", "retrieve"],
    tags=["extraction", "information", "data", "parsing"]
)
async def extract(
    context: SkillContext,
    content: str,
    target: str,
    format_hint: Optional[str] = None,
    schema: Optional[Dict[str, str]] = None
) -> SkillResult[Dict[str, Any]]:
    """
    Extract specific information from content.
    
    This cognitive skill focuses on pulling out targeted information
    from content based on the specified extraction target.
    
    Args:
        context: Skill execution context
        content: Content to extract from
        target: What to extract (e.g., "key_points", "dates", "names")
        format_hint: Optional hint about expected format
        schema: Optional schema for structured extraction
        
    Returns:
        SkillResult with extracted data
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
    
    if not target:
        return SkillResult(
            status=SkillStatus.FAILED,
            confidence=0.0,
            errors=[SkillError(
                error_type="validation_error",
                message="No extraction target specified",
                recoverable=False
            )]
        )
    
    try:
        # Get extraction tool
        extraction_tool = get_tool(ContentExtractionTool)
        
        # Cognitive decision: What type of extraction should I perform?
        if schema:
            # Structured extraction
            logger.info(f"Performing structured extraction with schema: {list(schema.keys())}")
            result = await extraction_tool.extract_structured(content, schema)
        elif target.lower() in ["key_points", "main_points", "highlights"]:
            # Key points extraction
            logger.info("Performing key points extraction")
            result = await extraction_tool.extract_key_points(content)
        elif target.lower() in ["entities", "names", "people", "places", "organizations"]:
            # Entity extraction
            logger.info("Performing entity extraction")
            entity_types = _determine_entity_types(target)
            result = await extraction_tool.extract_entities(content, entity_types)
        else:
            # General extraction
            logger.info(f"Performing general extraction for: {target}")
            result = await extraction_tool.extract_information(content, target, format_hint)
        
        # Convert tool result to skill result
        extraction_data = {
            "target": target,
            "extracted": result.extracted_data,
            "format_hint": format_hint,
            "schema": schema
        }
        
        return SkillResult(
            data=extraction_data,
            status=SkillStatus.COMPLETED,
            confidence=result.confidence,
            metadata={
                "content_length": len(content),
                "target": target,
                "extraction_method": result.metadata.get("method", "unknown"),
                "tool_metadata": result.metadata
            }
        )
        
    except Exception as e:
        logger.error(f"Extraction skill failed: {e}")
        
        # Attempt graceful degradation
        try:
            # Try basic pattern-based extraction
            basic_extraction = _basic_content_extraction(content, target)
            
            return SkillResult(
                data=basic_extraction,
                status=SkillStatus.COMPLETED,
                confidence=0.3,  # Low confidence for fallback
                metadata={"fallback": True, "original_error": str(e)},
                errors=[SkillError(
                    error_type="tool_failure",
                    message=f"Primary extraction failed, used fallback: {str(e)}",
                    recoverable=True
                )]
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback extraction also failed: {fallback_error}")
            
            return SkillResult(
                status=SkillStatus.FAILED,
                confidence=0.0,
                errors=[
                    SkillError(
                        error_type="skill_failure",
                        message=f"Both primary and fallback extraction failed: {str(e)}",
                        recoverable=True
                    )
                ]
            )


def _determine_entity_types(target: str) -> List[str]:
    """Determine entity types based on target."""
    target_lower = target.lower()
    
    if "people" in target_lower or "names" in target_lower or "person" in target_lower:
        return ["people", "names"]
    elif "places" in target_lower or "location" in target_lower:
        return ["places", "locations"]
    elif "organizations" in target_lower or "companies" in target_lower:
        return ["organizations", "companies"]
    else:
        return ["people", "places", "organizations"]


def _basic_content_extraction(content: str, target: str) -> Dict[str, Any]:
    """
    Basic content extraction fallback.
    
    Provides simple pattern-based extraction when sophisticated tools fail.
    """
    import re
    
    # Basic extraction patterns
    patterns = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "url": r'https?://[^\s]+',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "date": r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        "number": r'\b\d+(?:\.\d+)?\b',
    }
    
    extracted = {}
    
    # Try pattern matching
    for pattern_name, pattern in patterns.items():
        if pattern_name.lower() in target.lower():
            matches = re.findall(pattern, content, re.IGNORECASE)
            extracted[pattern_name] = matches
    
    # If no pattern matches, try basic text extraction
    if not extracted:
        # Extract sentences containing target keywords
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in target.lower().split()):
                relevant_sentences.append(sentence.strip())
        
        extracted["relevant_content"] = relevant_sentences[:3]  # Limit to 3 sentences
    
    return {
        "target": target,
        "extracted": extracted,
        "format_hint": None,
        "schema": None
    }