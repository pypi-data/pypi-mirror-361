"""
Cognitive skills for the architecture.

Skills represent cognitive operations - the mental processes of thinking.
"""

from .analyze import analyze
from .extract import extract
from .synthesize import synthesize
from .registry import (
    SkillRegistry,
    SkillFactory,
    SkillInfo,
    skill,
    get_skill_registry,
    create_skill_factory
)

__all__ = [
    "analyze",
    "extract", 
    "synthesize",
    "SkillRegistry",
    "SkillFactory",
    "SkillInfo",
    "skill",
    "get_skill_registry",
    "create_skill_factory",
]