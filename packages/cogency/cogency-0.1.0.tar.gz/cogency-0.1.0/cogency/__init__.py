"""
Cogency - Cognitive architecture for AI agents.

This package provides a clean, composable architecture for building AI agents
that mirrors human cognitive processes through Skills, Tools, and Services.
"""

from .core import (
    SkillResult,
    SkillError,
    SkillContext,
    SkillStatus,
)
from .registry import (
    ServiceRegistry,
    register_service,
    get_service,
)
from .skills import (
    analyze,
    extract,
    synthesize,
    SkillRegistry,
    SkillFactory,
    SkillInfo,
    skill,
    get_skill_registry,
    create_skill_factory,
)

__version__ = "0.1.0"
__all__ = [
    # Core types
    "SkillResult",
    "SkillError", 
    "SkillContext",
    "SkillStatus",
    # Registry
    "ServiceRegistry",
    "register_service",
    "get_service",
    # Skills
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