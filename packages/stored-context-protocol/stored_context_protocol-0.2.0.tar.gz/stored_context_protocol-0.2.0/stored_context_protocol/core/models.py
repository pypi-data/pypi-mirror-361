"""Data models for Stored Context Protocol."""

from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class Context:
    """Represents a single context with instructor information."""
    
    content: str
    instructor_name: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate and process context after initialization."""
        if not self.content:
            raise ValueError("Context content cannot be empty")
        
        # Generate ID based on content
        self.id = hashlib.md5(self.content.encode()).hexdigest()[:8]
        
        # Set defaults if not provided
        if not self.instructor_name:
            if self.file_path:
                # Extract filename without extension as instructor name
                import os
                self.instructor_name = os.path.splitext(os.path.basename(self.file_path))[0]
            else:
                raise ValueError("Instructor name must be provided for text content")
        
        if not self.description:
            # Generate description from available information
            if self.file_path and self.instructor_name:
                self.description = f"{self.instructor_name} - {self.file_path}"
            elif self.instructor_name:
                self.description = f"Context for {self.instructor_name}"
            else:
                self.description = "Unnamed context"
    
    def to_dict(self):
        """Convert context to dictionary representation."""
        return {
            "id": self.id,
            "instructor_name": self.instructor_name,
            "description": self.description,
            "file_path": self.file_path,
            "content_preview": self.content[:100] + "..." if len(self.content) > 100 else self.content
        }