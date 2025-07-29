"""
Base classes for the cognitive architecture.

Provides the foundational interfaces for Skills, Tools, and Services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
import time
import logging

from .result import SkillResult, SkillError, SkillStatus
from .context import SkillContext

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseService(ABC):
    """
    Base class for all services.
    
    Services provide raw capabilities - they execute commands without
    cognitive logic or decision making.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"cogency.service.{name}")
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy and available."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
        }


class BaseTool(ABC):
    """
    Base class for all tools.
    
    Tools provide task-specific wrappers around services with added
    functionality like caching, validation, and retry logic.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"cogency.tool.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult[Any]:
        """Execute the tool's primary operation."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
        }


class BaseSkill(ABC, Generic[T]):
    """
    Base class for all skills.
    
    Skills represent cognitive operations that orchestrate tools to
    achieve specific mental processes.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"cogency.skill.{name}")
    
    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult[T]:
        """Execute the cognitive operation."""
        pass
    
    async def pre_execute(self, context: SkillContext) -> None:
        """Hook called before execution."""
        self.logger.debug(f"Starting {self.name} execution")
        context.add_to_history({
            "skill": self.name,
            "timestamp": time.time(),
            "phase": "pre_execute",
        })
    
    async def post_execute(self, result: SkillResult[T], context: SkillContext) -> None:
        """Hook called after execution."""
        self.logger.debug(f"Completed {self.name} execution: {result.status}")
        context.add_to_history({
            "skill": self.name,
            "timestamp": time.time(),
            "phase": "post_execute",
            "status": result.status.value,
            "confidence": result.confidence,
        })
    
    async def handle_error(
        self, 
        error: Exception, 
        context: SkillContext
    ) -> SkillResult[T]:
        """Handle errors during execution."""
        self.logger.error(f"Error in {self.name}: {error}")
        
        skill_error = SkillError(
            error_type=error.__class__.__name__,
            message=str(error),
            recoverable=True,  # Most errors are recoverable
            details={"skill": self.name}
        )
        
        return SkillResult.failure(skill_error)
    
    def get_info(self) -> Dict[str, Any]:
        """Get skill information."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
        }


def skill(name: str):
    """
    Decorator to register a skill function.
    
    Transforms a function into a skill that can be used in the
    cognitive architecture.
    """
    def decorator(func):
        async def wrapper(context: SkillContext, **kwargs) -> SkillResult[Any]:
            start_time = time.time()
            
            try:
                # Execute the function
                result = await func(context, **kwargs)
                
                # Ensure it's a SkillResult
                if not isinstance(result, SkillResult):
                    result = SkillResult.success(result)
                
                # Add execution time
                result.execution_time = time.time() - start_time
                
                return result
                
            except Exception as e:
                logger.error(f"Error in skill {name}: {e}")
                return SkillResult.failure(
                    SkillError(
                        error_type=e.__class__.__name__,
                        message=str(e),
                        recoverable=True,
                    ),
                    execution_time=time.time() - start_time,
                )
        
        wrapper.__name__ = name
        wrapper.__doc__ = func.__doc__
        wrapper.skill_name = name
        
        return wrapper
    
    return decorator