"""Main context management class."""

import os
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from .models import Context
from .context_selector import ContextSelector
from ..utils.file_loader import FileLoader
from ..exceptions import ContextNotFoundError


class ContextManager:
    """Manages multiple contexts and provides selection functionality."""
    
    def __init__(self, openai_api_key: Optional[str] = None,
                 openai_base_url: Optional[str] = None,
                 openai_model: Optional[str] = None):
        """
        Initialize the ContextManager.
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            openai_base_url: OpenAI base URL (defaults to OPENAI_BASE_URL env var)
            openai_model: Default model to use (defaults to OPENAI_MODEL env var)
        """
        self.contexts: List[Context] = []
        self.context_selector = ContextSelector(
            api_key=openai_api_key,
            base_url=openai_base_url,
            default_model=openai_model
        )
        self.file_loader = FileLoader()
    
    def load_file(self, file_path: str, instructor_name: Optional[str] = None, 
                  description: Optional[str] = None) -> Context:
        """
        Load context from a file.
        
        Args:
            file_path: Path to the file (.txt or .md)
            instructor_name: Optional instructor name (uses filename if not provided)
            description: Optional description
            
        Returns:
            Created Context object
        """
        content = self.file_loader.load_file(file_path)
        
        context = Context(
            content=content,
            instructor_name=instructor_name,
            description=description,
            file_path=file_path
        )
        
        self.contexts.append(context)
        return context
    
    def load_text(self, text: str, instructor_name: str, 
                  description: Optional[str] = None) -> Context:
        """
        Load context from text.
        
        Args:
            text: The context text
            instructor_name: Instructor name (required for text)
            description: Optional description
            
        Returns:
            Created Context object
        """
        context = Context(
            content=text,
            instructor_name=instructor_name,
            description=description
        )
        
        self.contexts.append(context)
        return context
    
    def load_directory(self, directory_path: str, 
                      instructor_mapping: Optional[Dict[str, str]] = None) -> List[Context]:
        """
        Load all valid files from a directory.
        
        Args:
            directory_path: Path to directory containing context files
            instructor_mapping: Optional dict mapping filenames to instructor names
            
        Returns:
            List of created Context objects
        """
        loaded_contexts = []
        path = Path(directory_path)
        
        for file_path in path.iterdir():
            if file_path.suffix in ['.txt', '.md']:
                instructor_name = None
                if instructor_mapping and file_path.name in instructor_mapping:
                    instructor_name = instructor_mapping[file_path.name]
                
                try:
                    context = self.load_file(str(file_path), instructor_name)
                    loaded_contexts.append(context)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")
        
        return loaded_contexts
    
    def get_context_count(self) -> int:
        """Get the number of loaded contexts."""
        return len(self.contexts)
    
    def get_all_instructors(self) -> List[Dict[str, str]]:
        """
        Get all instructor information.
        
        Returns:
            List of dictionaries with instructor information
        """
        return [
            {
                "instructor_name": ctx.instructor_name,
                "description": ctx.description,
                "id": ctx.id
            }
            for ctx in self.contexts
        ]
    
    async def select_context_async(self, prompt: str) -> Dict[str, Any]:
        """
        Select the most relevant context based on the prompt (async).
        
        Args:
            prompt: The user's prompt
            
        Returns:
            Dictionary with selected context information
        """
        if not self.contexts:
            raise ContextNotFoundError("No contexts loaded")
        
        # Get instructor options for function call
        instructor_options = [
            {
                "name": ctx.instructor_name,
                "description": ctx.description
            }
            for ctx in self.contexts
        ]
        
        # Use context selector to find best match
        selected_instructor = await self.context_selector.select_instructor_async(
            prompt, instructor_options
        )
        
        # Find the matching context
        selected_context = None
        for ctx in self.contexts:
            if ctx.instructor_name == selected_instructor:
                selected_context = ctx
                break
        
        if not selected_context:
            raise ContextNotFoundError(f"Context for instructor '{selected_instructor}' not found")
        
        return {
            "instructor_name": selected_context.instructor_name,
            "description": selected_context.description,
            "context_id": selected_context.id,
            "file_path": selected_context.file_path
        }
    
    def select_context(self, prompt: str) -> Dict[str, Any]:
        """
        Select the most relevant context based on the prompt (sync).
        
        Args:
            prompt: The user's prompt
            
        Returns:
            Dictionary with selected context information
        """
        if not self.contexts:
            raise ContextNotFoundError("No contexts loaded")
        
        # Get instructor options for function call
        instructor_options = [
            {
                "name": ctx.instructor_name,
                "description": ctx.description
            }
            for ctx in self.contexts
        ]
        
        # Use context selector to find best match
        selected_instructor = self.context_selector.select_instructor(
            prompt, instructor_options
        )
        
        # Find the matching context
        selected_context = None
        for ctx in self.contexts:
            if ctx.instructor_name == selected_instructor:
                selected_context = ctx
                break
        
        if not selected_context:
            raise ContextNotFoundError(f"Context for instructor '{selected_instructor}' not found")
        
        return {
            "instructor_name": selected_context.instructor_name,
            "description": selected_context.description,
            "context_id": selected_context.id,
            "file_path": selected_context.file_path
        }
    
    def build_prompt_with_context(self, prompt: str, instructor_name: str) -> str:
        """
        Build a complete prompt with the selected context.
        
        Args:
            prompt: The original user prompt
            instructor_name: The selected instructor name
            
        Returns:
            Combined prompt with context
        """
        # Find the context
        selected_context = None
        for ctx in self.contexts:
            if ctx.instructor_name == instructor_name:
                selected_context = ctx
                break
        
        if not selected_context:
            raise ContextNotFoundError(f"Context for instructor '{instructor_name}' not found")
        
        # Combine context and prompt with newline
        return f"{selected_context.content}\n{prompt}"
    
    def clear_contexts(self):
        """Clear all loaded contexts."""
        self.contexts.clear()
    
    def remove_context(self, instructor_name: str):
        """Remove a specific context by instructor name."""
        self.contexts = [
            ctx for ctx in self.contexts 
            if ctx.instructor_name != instructor_name
        ]
    
    def export_contexts(self, output_path: str):
        """Export all contexts to a JSON file."""
        data = {
            "contexts": [ctx.to_dict() for ctx in self.contexts],
            "count": len(self.contexts)
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)