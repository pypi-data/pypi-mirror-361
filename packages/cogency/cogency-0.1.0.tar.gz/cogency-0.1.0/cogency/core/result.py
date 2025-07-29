"""
Result types for cognitive operations.

Defines the standard result format for all skills and tools.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")


class SkillStatus(Enum):
    """Status of a skill execution."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillError:
    """Error information for skill execution."""
    
    error_type: str
    message: str
    recoverable: bool
    details: Optional[Dict[str, Any]] = None


@dataclass
class SkillResult(Generic[T]):
    """
    Standard result format for all cognitive operations.
    
    Provides consistent structure for skill outputs with metadata,
    error handling, and composability.
    """
    
    # Core result data
    data: Optional[T] = None
    status: SkillStatus = SkillStatus.PENDING
    confidence: float = 0.0
    
    # Metadata
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Error handling
    errors: List[SkillError] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def is_success(self) -> bool:
        """Check if the skill execution was successful."""
        return self.status == SkillStatus.COMPLETED and not self.errors
    
    @property
    def is_failure(self) -> bool:
        """Check if the skill execution failed."""
        return self.status == SkillStatus.FAILED
    
    @property
    def is_recoverable(self) -> bool:
        """Check if any errors are recoverable."""
        return any(error.recoverable for error in self.errors)
    
    def add_error(self, error: SkillError) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        if self.status == SkillStatus.COMPLETED:
            self.status = SkillStatus.FAILED
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the result."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "data": self.data,
            "status": self.status.value,
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "errors": [
                {
                    "error_type": error.error_type,
                    "message": error.message,
                    "recoverable": error.recoverable,
                    "details": error.details,
                }
                for error in self.errors
            ],
        }
    
    @classmethod
    def success(cls, data: T, confidence: float = 1.0, **kwargs) -> "SkillResult[T]":
        """Create a successful result."""
        return cls(
            data=data,
            status=SkillStatus.COMPLETED,
            confidence=confidence,
            **kwargs
        )
    
    @classmethod
    def failure(cls, error: SkillError, **kwargs) -> "SkillResult[T]":
        """Create a failed result."""
        return cls(
            status=SkillStatus.FAILED,
            errors=[error],
            **kwargs
        )
    
    @classmethod
    def pending(cls, **kwargs) -> "SkillResult[T]":
        """Create a pending result."""
        return cls(
            status=SkillStatus.PENDING,
            **kwargs
        )