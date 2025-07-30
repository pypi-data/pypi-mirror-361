"""
Storage implementation for managing contexts.
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path
from threading import Lock

from .models import Context, InstructorInfo
from .exceptions import ContextNotFoundError, SCPError


class ContextStorage:
    """Thread-safe storage for contexts."""
    
    def __init__(self, max_contexts: int = 100, persist_file: Optional[str] = None):
        """
        Initialize context storage.
        
        Args:
            max_contexts: Maximum number of contexts to store
            persist_file: Optional file path to persist contexts
        """
        self.max_contexts = max_contexts
        self.persist_file = persist_file
        self._contexts: Dict[str, Context] = {}
        self._lock = Lock()
        
        # Load from persistence if available
        if persist_file and os.path.exists(persist_file):
            self._load_from_file()
    
    def add_context(self, context: Context) -> str:
        """
        Add a new context to storage.
        
        Args:
            context: Context to add
            
        Returns:
            Context ID
        """
        with self._lock:
            # Check if we've reached the limit
            if len(self._contexts) >= self.max_contexts:
                # Remove the oldest context
                oldest_id = min(
                    self._contexts.keys(),
                    key=lambda k: self._contexts[k].created_at
                )
                del self._contexts[oldest_id]
            
            # Add the new context
            self._contexts[context.id] = context
            
            # Persist if enabled
            if self.persist_file:
                self._save_to_file()
            
            return context.id
    
    def get_context(self, context_id: str) -> Context:
        """
        Retrieve a context by ID.
        
        Args:
            context_id: ID of the context to retrieve
            
        Returns:
            The requested Context
            
        Raises:
            ContextNotFoundError: If context not found
        """
        with self._lock:
            if context_id not in self._contexts:
                raise ContextNotFoundError(f"Context with ID '{context_id}' not found")
            return self._contexts[context_id]
    
    def remove_context(self, context_id: str) -> bool:
        """
        Remove a context from storage.
        
        Args:
            context_id: ID of the context to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if context_id in self._contexts:
                del self._contexts[context_id]
                
                # Persist if enabled
                if self.persist_file:
                    self._save_to_file()
                
                return True
            return False
    
    def list_contexts(self) -> List[InstructorInfo]:
        """
        List all contexts as InstructorInfo objects.
        
        Returns:
            List of InstructorInfo objects
        """
        with self._lock:
            return [
                context.to_instructor_info()
                for context in sorted(
                    self._contexts.values(),
                    key=lambda x: x.created_at,
                    reverse=True
                )
            ]
    
    def get_context_count(self) -> int:
        """Get the number of stored contexts."""
        with self._lock:
            return len(self._contexts)
    
    def clear_all(self) -> None:
        """Clear all stored contexts."""
        with self._lock:
            self._contexts.clear()
            
            # Persist if enabled
            if self.persist_file:
                self._save_to_file()
    
    def get_all_contexts(self) -> List[Context]:
        """Get all stored contexts."""
        with self._lock:
            return list(self._contexts.values())
    
    def _save_to_file(self) -> None:
        """Save contexts to persistence file."""
        try:
            data = {
                "contexts": [
                    context.to_dict()
                    for context in self._contexts.values()
                ]
            }
            
            # Ensure directory exists
            Path(self.persist_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.persist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise SCPError(f"Failed to save contexts: {e}")
    
    def _load_from_file(self) -> None:
        """Load contexts from persistence file."""
        try:
            with open(self.persist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for context_data in data.get("contexts", []):
                context = Context.from_dict(context_data)
                self._contexts[context.id] = context
        except Exception as e:
            raise SCPError(f"Failed to load contexts: {e}")