"""
Core implementation of the Stored Context Protocol.
"""

import os
import json
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
import hashlib

from .models import Context, InstructorInfo
from .storage import ContextStorage
from .openai_handler import OpenAIHandler
from .exceptions import SCPError, ContextNotFoundError
from .utils import extract_file_name, generate_description


class StoredContextProtocol:
    """Main class for managing and retrieving stored contexts."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4-0125-preview",
        max_contexts: int = 100
    ):
        """
        Initialize the Stored Context Protocol.
        
        Args:
            api_key: OpenAI API key (can also be set via OPENAI_API_KEY env var)
            base_url: OpenAI base URL (can also be set via OPENAI_BASE_URL env var)
            model: OpenAI model to use (default: gpt-4-0125-preview)
            max_contexts: Maximum number of contexts to store (default: 100)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self.max_contexts = max_contexts
        
        if not self.api_key:
            raise SCPError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.storage = ContextStorage(max_contexts=max_contexts)
        self.openai_handler = OpenAIHandler(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model
        )
    
    def load_file(
        self,
        file_path: Union[str, Path],
        instructor_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Load context from a file (.txt or .md).
        
        Args:
            file_path: Path to the file to load
            instructor_name: Name for this context (defaults to filename)
            description: Description of the context (auto-generated if not provided)
            
        Returns:
            Context ID for reference
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise SCPError(f"File not found: {file_path}")
        
        if file_path.suffix not in ['.txt', '.md']:
            raise SCPError("Only .txt and .md files are supported")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use filename as instructor name if not provided
        if instructor_name is None:
            instructor_name = extract_file_name(file_path)
        
        # Generate description if not provided
        if description is None:
            description = generate_description(instructor_name, file_path)
        
        return self.load_text(content, instructor_name, description)
    
    def load_text(
        self,
        text: str,
        instructor_name: str,
        description: Optional[str] = None
    ) -> str:
        """
        Load context from text.
        
        Args:
            text: The context text to store
            instructor_name: Name for this context (required for text)
            description: Description of the context (auto-generated if not provided)
            
        Returns:
            Context ID for reference
        """
        if not instructor_name:
            raise SCPError("instructor_name is required when loading text")
        
        if not text.strip():
            raise SCPError("Context text cannot be empty")
        
        # Generate description if not provided
        if description is None:
            description = generate_description(instructor_name)
        
        # Create context object
        context = Context(
            instructor_name=instructor_name,
            content=text,
            description=description
        )
        
        # Store context
        context_id = self.storage.add_context(context)
        
        return context_id
    
    def select_context(self, prompt: str, max_selections: int = 1) -> Dict[str, Any]:
        """
        Select the most relevant context for a given prompt.
        
        Args:
            prompt: The user's query
            max_selections: Maximum number of contexts to select
            
        Returns:
            Dictionary containing selected context information
        """
        instructor_infos = self.storage.list_contexts()
        
        if not instructor_infos:
            raise SCPError("No contexts loaded. Please load contexts first.")
        
        # Use OpenAI function calling to select relevant contexts
        selected_ids = self.openai_handler.select_relevant_contexts(
            prompt=prompt,
            instructor_infos=instructor_infos,
            max_selections=max_selections
        )
        
        if not selected_ids:
            # If no context selected, return the first one as fallback
            selected_ids = [instructor_infos[0].id]
        
        # Get the first selected context
        context = self.storage.get_context(selected_ids[0])
        
        return {
            "id": context.id,
            "instructor_name": context.instructor_name,
            "description": context.description,
            "content": context.content
        }
    
    def build_prompt_with_context(
        self,
        prompt: str,
        instructor_name: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> str:
        """
        Build a prompt with the specified context.
        
        Args:
            prompt: The user's original prompt
            instructor_name: Name of the instructor to use (searches for matching context)
            context_id: Direct context ID to use (takes precedence over instructor_name)
            
        Returns:
            The complete prompt with context
        """
        context = None
        
        if context_id:
            # Use context ID directly
            context = self.storage.get_context(context_id)
        elif instructor_name:
            # Find context by instructor name
            for ctx in self.storage.get_all_contexts():
                if ctx.instructor_name == instructor_name:
                    context = ctx
                    break
            
            if not context:
                raise ContextNotFoundError(f"No context found with instructor name: {instructor_name}")
        else:
            raise SCPError("Either instructor_name or context_id must be provided")
        
        # Build prompt with context
        return f"{context.content}\n\n{prompt}"
    
    def get_context(self, context_id: str) -> Context:
        """
        Retrieve a specific context by ID.
        
        Args:
            context_id: The ID of the context to retrieve
            
        Returns:
            The requested Context object
        """
        return self.storage.get_context(context_id)
    
    def list_contexts(self) -> List[InstructorInfo]:
        """
        List all available contexts with their metadata.
        
        Returns:
            List of InstructorInfo objects
        """
        return self.storage.list_contexts()
    
    def remove_context(self, context_id: str) -> bool:
        """
        Remove a context from storage.
        
        Args:
            context_id: The ID of the context to remove
            
        Returns:
            True if removed successfully
        """
        return self.storage.remove_context(context_id)
    
    def clear_all_contexts(self) -> None:
        """Clear all stored contexts."""
        self.storage.clear_all()
    
    def query_with_context(
        self,
        prompt: str,
        auto_select_context: bool = True,
        context_ids: Optional[List[str]] = None,
        max_contexts_to_use: int = 1
    ) -> Dict[str, Any]:
        """
        Query OpenAI with automatic or manual context selection.
        
        Args:
            prompt: The user's query/prompt
            auto_select_context: Whether to automatically select relevant context
            context_ids: Manual list of context IDs to include (overrides auto_select)
            max_contexts_to_use: Maximum number of contexts to include (for auto selection)
            
        Returns:
            Dictionary containing:
                - response: The OpenAI response
                - selected_contexts: List of selected context info
                - full_prompt: The complete prompt sent to OpenAI
        """
        selected_contexts = []
        
        if context_ids:
            # Manual context selection
            for context_id in context_ids:
                try:
                    context = self.storage.get_context(context_id)
                    selected_contexts.append(context)
                except ContextNotFoundError:
                    pass  # Skip missing contexts
        
        elif auto_select_context and self.storage.get_context_count() > 0:
            # Automatic context selection using function calling
            instructor_infos = self.storage.list_contexts()
            
            if instructor_infos:
                # Use OpenAI function calling to select relevant contexts
                selected_ids = self.openai_handler.select_relevant_contexts(
                    prompt=prompt,
                    instructor_infos=instructor_infos,
                    max_selections=max_contexts_to_use
                )
                
                # Retrieve selected contexts
                for context_id in selected_ids:
                    try:
                        context = self.storage.get_context(context_id)
                        selected_contexts.append(context)
                    except ContextNotFoundError:
                        pass
        
        # Build the full prompt
        full_prompt = self._build_prompt(prompt, selected_contexts)
        
        # Get response from OpenAI
        response = self.openai_handler.get_completion(full_prompt)
        
        # Prepare result
        result = {
            "response": response,
            "selected_contexts": [
                {
                    "id": ctx.id,
                    "instructor_name": ctx.instructor_name,
                    "description": ctx.description
                }
                for ctx in selected_contexts
            ],
            "full_prompt": full_prompt
        }
        
        return result
    
    def _build_prompt(self, user_prompt: str, contexts: List[Context]) -> str:
        """
        Build the complete prompt with contexts.
        
        Args:
            user_prompt: The user's original prompt
            contexts: List of Context objects to include
            
        Returns:
            The complete prompt with contexts
        """
        if not contexts:
            return user_prompt
        
        # Build prompt with contexts
        parts = []
        
        # Add each context
        for context in contexts:
            parts.append(context.content)
        
        # Add user prompt with separator
        parts.append(user_prompt)
        
        # Join with newlines
        return "\n\n".join(parts)
    
    def set_model(self, model: str) -> None:
        """Update the OpenAI model."""
        self.model = model
        self.openai_handler.model = model
    
    def set_api_key(self, api_key: str) -> None:
        """Update the OpenAI API key."""
        self.api_key = api_key
        self.openai_handler.api_key = api_key
    
    def set_base_url(self, base_url: str) -> None:
        """Update the OpenAI base URL."""
        self.base_url = base_url
        self.openai_handler.base_url = base_url