"""
Core types and interfaces for Cogency.

This module defines the fundamental building blocks of the cognitive architecture.
"""

from .result import SkillResult, SkillError, SkillStatus
from .context import SkillContext
from .base import BaseSkill, BaseService, BaseTool
from .workflow import CognitiveContext, WorkflowStatus, Exchange, MemorySnapshot

__all__ = [
    "SkillResult",
    "SkillError", 
    "SkillStatus",
    "SkillContext",
    "BaseSkill",
    "BaseService",
    "BaseTool",
    "CognitiveContext",
    "WorkflowStatus",
    "Exchange",
    "MemorySnapshot",
]