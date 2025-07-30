"""
Data models for the Stored Context Protocol.
"""

from dataclasses import dataclass, field
from typing import Optional
import hashlib
from datetime import datetime


@dataclass
class InstructorInfo:
    """Metadata about a stored context for function calling."""
    id: str
    instructor_name: str
    description: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "instructor_name": self.instructor_name,
            "description": self.description
        }


@dataclass
class Context:
    """Complete context including content and metadata."""
    instructor_name: str
    content: str
    description: str
    id: str = field(default="", init=False)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Generate ID after initialization."""
        if not self.id:
            # Generate unique ID based on content and instructor name
            hash_input = f"{self.instructor_name}:{self.content[:100]}"
            self.id = hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def to_instructor_info(self) -> InstructorInfo:
        """Convert to InstructorInfo for listings."""
        return InstructorInfo(
            id=self.id,
            instructor_name=self.instructor_name,
            description=self.description
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "instructor_name": self.instructor_name,
            "content": self.content,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Context":
        """Create Context from dictionary."""
        context = cls(
            instructor_name=data["instructor_name"],
            content=data["content"],
            description=data["description"]
        )
        context.id = data["id"]
        context.created_at = datetime.fromisoformat(data["created_at"])
        return context