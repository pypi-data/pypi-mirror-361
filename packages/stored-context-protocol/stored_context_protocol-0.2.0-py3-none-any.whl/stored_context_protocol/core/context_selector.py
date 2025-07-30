"""Context selection using OpenAI function calling."""

import os
import json
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI, AsyncOpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from ..exceptions import OpenAIError


class ContextSelector:
    """Handles context selection using OpenAI function calling."""
    
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
        self.default_model = default_model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not api_key:
            raise OpenAIError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Create clients with optional base_url
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)
    
    def _create_function_schema(self, instructor_options: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create the function schema for OpenAI function calling."""
        # Create enum of instructor names
        instructor_names = [opt["name"] for opt in instructor_options]
        
        return {
            "name": "select_instructor",
            "description": "Select the most relevant instructor based on the user's prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "instructor_name": {
                        "type": "string",
                        "enum": instructor_names,
                        "description": "The name of the most relevant instructor"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why this instructor was selected"
                    }
                },
                "required": ["instructor_name", "reasoning"]
            }
        }
    
    def _create_system_prompt(self, instructor_options: List[Dict[str, str]]) -> str:
        """Create system prompt with instructor information."""
        instructor_info = "\n".join([
            f"- {opt['name']}: {opt['description']}"
            for opt in instructor_options
        ])
        
        return f"""You are a context selector. Based on the user's prompt, select the most relevant instructor from the available options.

Available instructors:
{instructor_info}

Analyze the user's prompt and select the instructor whose expertise best matches the query."""
    
    async def select_instructor_async(self, prompt: str, 
                                     instructor_options: List[Dict[str, str]],
                                     model: Optional[str] = None) -> str:
        """
        Select the most relevant instructor asynchronously.
        
        Args:
            prompt: User's prompt
            instructor_options: List of available instructors with descriptions
            model: Model to use (defaults to configured model)
            
        Returns:
            Selected instructor name
        """
        try:
            # Use provided model or fall back to default
            model = model or self.default_model
            
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_system_prompt(instructor_options)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                functions=[self._create_function_schema(instructor_options)],
                function_call={"name": "select_instructor"}
            )
            
            # Extract function call result
            function_call = response.choices[0].message.function_call
            if function_call:
                result = json.loads(function_call.arguments)
                return result["instructor_name"]
            else:
                raise OpenAIError("No function call in response")
                
        except Exception as e:
            raise OpenAIError(f"Failed to select instructor: {str(e)}")
    
    def select_instructor(self, prompt: str, 
                         instructor_options: List[Dict[str, str]],
                         model: Optional[str] = None) -> str:
        """
        Select the most relevant instructor synchronously.
        
        Args:
            prompt: User's prompt
            instructor_options: List of available instructors with descriptions
            model: Model to use (defaults to configured model)
            
        Returns:
            Selected instructor name
        """
        try:
            # Use provided model or fall back to default
            model = model or self.default_model
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_system_prompt(instructor_options)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                functions=[self._create_function_schema(instructor_options)],
                function_call={"name": "select_instructor"}
            )
            
            # Extract function call result
            function_call = response.choices[0].message.function_call
            if function_call:
                result = json.loads(function_call.arguments)
                return result["instructor_name"]
            else:
                raise OpenAIError("No function call in response")
                
        except Exception as e:
            raise OpenAIError(f"Failed to select instructor: {str(e)}")