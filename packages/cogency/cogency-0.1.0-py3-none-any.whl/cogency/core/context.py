"""
Context for cognitive operations.

Provides the execution environment and dependencies for skills.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class SkillContext:
    """
    Context for skill execution.
    
    Contains the environment, dependencies, and state needed for
    cognitive operations to execute properly.
    """
    
    # Core context
    user_intent: str = ""
    session_id: str = ""
    
    # Execution parameters
    requires_deep_analysis: bool = False
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    
    # State and history
    state: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Dependencies (injected by registry)
    services: Dict[str, Any] = field(default_factory=dict)
    tools: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_service(self, service_type: type) -> Any:
        """Get a service by type."""
        service_name = service_type.__name__
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not available in context")
        return self.services[service_name]
    
    def get_tool(self, tool_type: type) -> Any:
        """Get a tool by type."""
        tool_name = tool_type.__name__
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not available in context")
        return self.tools[tool_name]
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value."""
        self.state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self.state.get(key, default)
    
    def add_to_history(self, entry: Dict[str, Any]) -> None:
        """Add an entry to the execution history."""
        self.history.append(entry)
    
    def clone(self, **updates) -> "SkillContext":
        """Create a copy of the context with optional updates."""
        new_context = SkillContext(
            user_intent=self.user_intent,
            session_id=self.session_id,
            requires_deep_analysis=self.requires_deep_analysis,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            state=self.state.copy(),
            history=self.history.copy(),
            services=self.services.copy(),
            tools=self.tools.copy(),
            metadata=self.metadata.copy(),
        )
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(new_context, key):
                setattr(new_context, key, value)
        
        return new_context