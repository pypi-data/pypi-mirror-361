"""
Content extraction tool.

Provides smart extraction capabilities with validation and structured output.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import asyncio
import re
import logging

from ..core.base import BaseTool
from ..services.llm import LLMService

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result from content extraction."""
    
    extracted_data: Dict[str, Any]
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ContentExtractionTool(BaseTool):
    """
    Smart content extraction tool with validation and structured output.
    
    Orchestrates LLM service to extract specific information from content
    with fallback strategies and validation.
    """
    
    def __init__(self, llm_service: LLMService):
        super().__init__("content_extraction")
        self.llm = llm_service
        self._extraction_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://[^\s]+',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        }
    
    async def extract_information(
        self, 
        content: str, 
        target: str,
        format_hint: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract specific information from content.
        
        Args:
            content: Text content to extract from
            target: What to extract (e.g., "key_points", "dates", "names")
            format_hint: Optional hint about expected format
            
        Returns:
            ExtractionResult with extracted data
        """
        # Input validation
        if not content or not content.strip():
            return ExtractionResult(
                extracted_data={"error": "empty_content"},
                confidence=0.0,
                metadata={"error": "No content provided"}
            )
        
        if not target:
            return ExtractionResult(
                extracted_data={"error": "no_target"},
                confidence=0.0,
                metadata={"error": "No extraction target specified"}
            )
        
        try:
            # Check if we have a pattern-based extraction
            if target.lower() in self._extraction_patterns:
                return await self._pattern_extract(content, target.lower())
            
            # Use LLM-based extraction
            return await self._llm_extract(content, target, format_hint)
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return ExtractionResult(
                extracted_data={"error": str(e)},
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def extract_structured(
        self, 
        content: str, 
        schema: Dict[str, str]
    ) -> ExtractionResult:
        """
        Extract structured data according to a schema.
        
        Args:
            content: Text content to extract from
            schema: Dictionary mapping field names to descriptions
            
        Returns:
            ExtractionResult with structured data
        """
        if not content or not content.strip():
            return ExtractionResult(
                extracted_data={},
                confidence=0.0,
                metadata={"error": "empty_content"}
            )
        
        if not schema:
            return ExtractionResult(
                extracted_data={},
                confidence=0.0,
                metadata={"error": "empty_schema"}
            )
        
        try:
            # Build extraction prompt
            schema_desc = "\n".join([
                f"- {field}: {description}" 
                for field, description in schema.items()
            ])
            
            extraction_prompt = f"""
            Extract the following information from the content:
            
            {schema_desc}
            
            Content:
            {content}
            
            Return the extracted information in a structured format.
            """
            
            result = await self.llm.extract(content, extraction_prompt)
            
            # Parse structured response
            extracted_data = self._parse_structured_response(result.content, schema)
            
            return ExtractionResult(
                extracted_data=extracted_data,
                confidence=result.confidence,
                metadata={
                    "schema": schema,
                    "method": "structured",
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            return ExtractionResult(
                extracted_data={},
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def extract_key_points(self, content: str, max_points: int = 5) -> ExtractionResult:
        """Extract key points from content."""
        try:
            result = await self.llm.extract(
                content, 
                f"key points (max {max_points})"
            )
            
            # Parse key points
            points = self._parse_key_points(result.content, max_points)
            
            return ExtractionResult(
                extracted_data={"key_points": points},
                confidence=result.confidence,
                metadata={"method": "key_points", "max_points": max_points}
            )
            
        except Exception as e:
            logger.error(f"Key points extraction failed: {e}")
            return ExtractionResult(
                extracted_data={"key_points": []},
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def extract_entities(self, content: str, entity_types: List[str]) -> ExtractionResult:
        """Extract named entities from content."""
        try:
            # Build entity extraction prompt
            entity_desc = ", ".join(entity_types)
            
            result = await self.llm.extract(
                content, 
                f"entities: {entity_desc}"
            )
            
            # Parse entities
            entities = self._parse_entities(result.content, entity_types)
            
            return ExtractionResult(
                extracted_data={"entities": entities},
                confidence=result.confidence,
                metadata={"method": "entities", "entity_types": entity_types}
            )
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return ExtractionResult(
                extracted_data={"entities": {}},
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def _pattern_extract(self, content: str, target: str) -> ExtractionResult:
        """Extract using regex patterns."""
        pattern = self._extraction_patterns.get(target)
        if not pattern:
            return ExtractionResult(
                extracted_data={"error": "pattern_not_found"},
                confidence=0.0,
                metadata={"error": f"No pattern for {target}"}
            )
        
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        return ExtractionResult(
            extracted_data={target: matches},
            confidence=1.0 if matches else 0.0,
            metadata={"method": "pattern", "pattern": pattern}
        )
    
    async def _llm_extract(
        self, 
        content: str, 
        target: str, 
        format_hint: Optional[str] = None
    ) -> ExtractionResult:
        """Extract using LLM."""
        extraction_target = target
        if format_hint:
            extraction_target = f"{target} ({format_hint})"
        
        result = await self.llm.extract(content, extraction_target)
        
        # Parse LLM response
        extracted_data = self._parse_llm_response(result.content, target)
        
        return ExtractionResult(
            extracted_data=extracted_data,
            confidence=result.confidence,
            metadata={
                "method": "llm",
                "target": target,
                "format_hint": format_hint
            }
        )
    
    def _parse_structured_response(
        self, 
        response: str, 
        schema: Dict[str, str]
    ) -> Dict[str, Any]:
        """Parse structured response from LLM."""
        # Simple parsing - can be enhanced with structured prompts
        extracted = {}
        
        for field in schema.keys():
            # Look for field in response
            pattern = rf'{field}[:\s]*([^\n]+)'
            match = re.search(pattern, response, re.IGNORECASE)
            
            if match:
                extracted[field] = match.group(1).strip()
            else:
                extracted[field] = None
        
        return extracted
    
    def _parse_key_points(self, response: str, max_points: int) -> List[str]:
        """Parse key points from response."""
        lines = response.strip().split('\n')
        points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                # Remove bullet point
                point = re.sub(r'^[-•*]\s*', '', line)
                points.append(point)
                
                if len(points) >= max_points:
                    break
        
        return points
    
    def _parse_entities(self, response: str, entity_types: List[str]) -> Dict[str, List[str]]:
        """Parse entities from response."""
        entities = {entity_type: [] for entity_type in entity_types}
        
        for entity_type in entity_types:
            # Look for entity type in response
            pattern = rf'{entity_type}[:\s]*([^\n]+)'
            match = re.search(pattern, response, re.IGNORECASE)
            
            if match:
                # Split by common separators
                entity_list = re.split(r'[,;]', match.group(1))
                entities[entity_type] = [e.strip() for e in entity_list if e.strip()]
        
        return entities
    
    def _parse_llm_response(self, response: str, target: str) -> Dict[str, Any]:
        """Parse general LLM response."""
        # Simple parsing - can be enhanced based on target type
        return {
            target: response.strip(),
            "raw_response": response
        }
    
    def add_extraction_pattern(self, name: str, pattern: str) -> None:
        """Add a new extraction pattern."""
        self._extraction_patterns[name] = pattern
        logger.info(f"Added extraction pattern: {name}")
    
    def get_available_patterns(self) -> List[str]:
        """Get list of available extraction patterns."""
        return list(self._extraction_patterns.keys())