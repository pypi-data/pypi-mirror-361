"""
Tools for the cognitive architecture.

Tools handle task-specific operations with smart behavior.
"""

from .content_analysis import ContentAnalysisTool
from .content_extraction import ContentExtractionTool

__all__ = [
    "ContentAnalysisTool",
    "ContentExtractionTool",
]