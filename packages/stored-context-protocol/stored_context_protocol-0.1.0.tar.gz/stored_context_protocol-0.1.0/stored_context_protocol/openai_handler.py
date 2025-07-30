"""
OpenAI API handler for context selection and completions.
"""

import json
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

from .models import InstructorInfo
from .exceptions import APIError


class OpenAIHandler:
    """Handler for OpenAI API interactions."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """
        Initialize OpenAI handler.
        
        Args:
            api_key: OpenAI API key
            base_url: OpenAI base URL
            model: Model to use for completions
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def select_relevant_contexts(
        self,
        prompt: str,
        instructor_infos: List[InstructorInfo],
        max_selections: int = 1
    ) -> List[str]:
        """
        Use OpenAI function calling to select relevant contexts.
        
        Args:
            prompt: User's query
            instructor_infos: Available contexts
            max_selections: Maximum number of contexts to select
            
        Returns:
            List of selected context IDs
        """
        try:
            # Prepare the function definition
            function_def = {
                "name": "select_contexts",
                "description": "Select the most relevant contexts based on the user's query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selected_contexts": {
                            "type": "array",
                            "description": "Array of selected context IDs",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Context ID"
                                    },
                                    "relevance_score": {
                                        "type": "number",
                                        "description": "Relevance score from 0 to 1"
                                    },
                                    "reason": {
                                        "type": "string",
                                        "description": "Brief reason for selection"
                                    }
                                },
                                "required": ["id", "relevance_score", "reason"]
                            }
                        }
                    },
                    "required": ["selected_contexts"]
                }
            }
            
            # Prepare context options for the prompt
            context_options = []
            for info in instructor_infos:
                context_options.append({
                    "id": info.id,
                    "name": info.instructor_name,
                    "description": info.description
                })
            
            # Create the system message
            system_message = f"""You are a context selection assistant. Based on the user's query, select up to {max_selections} most relevant contexts from the available options. Consider the instructor name and description to determine relevance."""
            
            # Create the user message
            user_message = f"""User Query: {prompt}

Available Contexts:
{json.dumps(context_options, indent=2)}

Select the most relevant contexts for answering this query."""
            
            # Make the API call with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                functions=[function_def],
                function_call={"name": "select_contexts"},
                temperature=0.3
            )
            
            # Parse the function call response
            if response.choices[0].message.function_call:
                function_args = json.loads(response.choices[0].message.function_call.arguments)
                selected = function_args.get("selected_contexts", [])
                
                # Sort by relevance score and limit to max_selections
                selected.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                selected = selected[:max_selections]
                
                # Return just the IDs
                return [ctx["id"] for ctx in selected]
            
            return []
            
        except Exception as e:
            raise APIError(f"Failed to select contexts: {str(e)}")
    
    def get_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Get a completion from OpenAI.
        
        Args:
            prompt: The complete prompt with contexts
            temperature: Temperature for generation
            
        Returns:
            The model's response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise APIError(f"Failed to get completion: {str(e)}")
    
    def update_client(self) -> None:
        """Update the OpenAI client with current settings."""
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )