"""
Core workflow abstractions for agent orchestration.

Provides minimal, reusable abstractions for cognitive workflows
without UI or application-specific coupling.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .result import SkillError


class WorkflowStatus(str, Enum):
    """Status of workflow execution."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Exchange(BaseModel):
    """Single exchange in conversation history."""
    
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class MemorySnapshot(BaseModel):
    """Snapshot of agent memory state."""
    
    facts: Dict[str, Any] = {}
    patterns: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


class CognitiveContext(BaseModel):
    """
    Minimal agent state for cognitive operations.
    
    Designed for composability and reusability across different
    agent architectures without UI or application coupling.
    """
    
    # Core input/output
    user_input: str = ""
    result: Optional[Any] = None
    
    # Conversation context
    history: List[Exchange] = []
    session_id: str = ""
    
    # Memory and context
    memory: MemorySnapshot = Field(default_factory=MemorySnapshot)
    context: Dict[str, Any] = {}
    
    # Execution state
    confidence: float = 0.0
    status: WorkflowStatus = WorkflowStatus.PENDING
    errors: List[SkillError] = []
    
    # Metadata
    metadata: Dict[str, Any] = {}
    start_time: datetime = Field(default_factory=datetime.now)
    
    def add_exchange(self, role: str, content: str) -> None:
        """Add an exchange to the conversation history."""
        self.history.append(Exchange(role=role, content=content))
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a context value."""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.context.get(key, default)
    
    def add_error(self, error: SkillError) -> None:
        """Add an error to the execution state."""
        self.errors.append(error)
        if self.status == WorkflowStatus.COMPLETED:
            self.status = WorkflowStatus.FAILED