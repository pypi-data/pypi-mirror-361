"""OpenAI integration helper utilities."""

import os
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from ..exceptions import OpenAIError


class OpenAIHelper:
    """Helper class for OpenAI operations."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None,
                 default_model: Optional[str] = None):
        """
        Initialize with OpenAI API key and optional configuration.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: OpenAI base URL (defaults to OPENAI_BASE_URL env var)
            default_model: Default model to use (defaults to OPENAI_MODEL env var)
        """
        # Use provided values or fall back to environment variables
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.default_model = default_model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        
        if not api_key:
            raise OpenAIError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Create clients with optional base_url
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)
    
    async def complete_with_context_async(self, prompt_with_context: str, 
                                         model: Optional[str] = None,
                                         **kwargs) -> str:
        """
        Get completion using the combined prompt and context asynchronously.
        
        Args:
            prompt_with_context: Combined prompt with context
            model: OpenAI model to use (defaults to configured model)
            **kwargs: Additional parameters for OpenAI API
            
        Returns:
            Model response
        """
        try:
            # Use provided model or fall back to default
            model = model or self.default_model
            
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_with_context}
                ],
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise OpenAIError(f"Failed to get completion: {str(e)}")
    
    def complete_with_context(self, prompt_with_context: str, 
                             model: Optional[str] = None,
                             **kwargs) -> str:
        """
        Get completion using the combined prompt and context synchronously.
        
        Args:
            prompt_with_context: Combined prompt with context
            model: OpenAI model to use (defaults to configured model)
            **kwargs: Additional parameters for OpenAI API
            
        Returns:
            Model response
        """
        try:
            # Use provided model or fall back to default
            model = model or self.default_model
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_with_context}
                ],
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise OpenAIError(f"Failed to get completion: {str(e)}")