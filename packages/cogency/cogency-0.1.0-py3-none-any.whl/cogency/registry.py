"""
Service registry for dependency injection.

Provides clean dependency management for the cognitive architecture.
"""

from typing import Type, Any, Dict, Optional, TypeVar, Callable
from dataclasses import dataclass
import threading
import logging

from .core.context import SkillContext

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ServiceBinding:
    """Represents a service binding in the registry."""
    
    service_type: Type
    instance: Any
    singleton: bool = True
    factory: Optional[Callable] = None


class ServiceRegistry:
    """
    Singleton service registry for dependency injection.
    
    Manages the lifecycle and injection of services and tools
    throughout the cognitive architecture.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._services: Dict[Type, ServiceBinding] = {}
                    cls._instance._tools: Dict[Type, ServiceBinding] = {}
                    cls._instance._initialized = False
        return cls._instance
    
    def register_service(self, service_type: Type[T], instance: T) -> None:
        """Register a service instance."""
        self._services[service_type] = ServiceBinding(
            service_type=service_type,
            instance=instance,
            singleton=True
        )
        logger.info(f"Registered service: {service_type.__name__}")
    
    def register_tool(self, tool_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a tool factory."""
        self._tools[tool_type] = ServiceBinding(
            service_type=tool_type,
            instance=None,
            singleton=True,
            factory=factory
        )
        logger.info(f"Registered tool: {tool_type.__name__}")
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        binding = self._services[service_type]
        return binding.instance
    
    def get_tool(self, tool_type: Type[T]) -> T:
        """Get a tool instance."""
        if tool_type not in self._tools:
            raise ValueError(f"Tool {tool_type.__name__} not registered")
        
        binding = self._tools[tool_type]
        
        # Create instance if needed
        if binding.instance is None and binding.factory:
            binding.instance = binding.factory()
        
        return binding.instance
    
    def create_context(
        self, 
        user_intent: str = "", 
        session_id: str = "",
        **kwargs
    ) -> SkillContext:
        """Create a skill context with injected dependencies."""
        context = SkillContext(
            user_intent=user_intent,
            session_id=session_id,
            **kwargs
        )
        
        # Inject services
        for service_type, binding in self._services.items():
            context.services[service_type.__name__] = binding.instance
        
        # Inject tools (lazily)
        for tool_type, binding in self._tools.items():
            if binding.instance is None and binding.factory:
                binding.instance = binding.factory()
            context.tools[tool_type.__name__] = binding.instance
        
        return context
    
    def is_service_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def is_tool_registered(self, tool_type: Type) -> bool:
        """Check if a tool type is registered."""
        return tool_type in self._tools
    
    def clear(self) -> None:
        """Clear all registered services and tools (for testing)."""
        self._services.clear()
        self._tools.clear()
        self._initialized = False
    
    def list_services(self) -> Dict[str, str]:
        """List all registered services."""
        return {
            service_type.__name__: binding.instance.__class__.__name__
            for service_type, binding in self._services.items()
        }
    
    def list_tools(self) -> Dict[str, str]:
        """List all registered tools."""
        return {
            tool_type.__name__: "factory" if binding.factory else "instance"
            for tool_type, binding in self._tools.items()
        }


# Global registry instance
_registry = ServiceRegistry()


def get_registry() -> ServiceRegistry:
    """Get the global service registry."""
    return _registry


def register_service(service_type: Type[T], instance: T) -> None:
    """Convenience function to register a service."""
    _registry.register_service(service_type, instance)


def register_tool(tool_type: Type[T], factory: Callable[[], T]) -> None:
    """Convenience function to register a tool."""
    _registry.register_tool(tool_type, factory)


def get_service(service_type: Type[T]) -> T:
    """Convenience function to get a service."""
    return _registry.get_service(service_type)


def get_tool(tool_type: Type[T]) -> T:
    """Convenience function to get a tool."""
    return _registry.get_tool(tool_type)


def create_context(user_intent: str = "", session_id: str = "", **kwargs) -> SkillContext:
    """Convenience function to create a context."""
    return _registry.create_context(user_intent, session_id, **kwargs)