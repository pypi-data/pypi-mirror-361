"""
Utility functions for the Stored Context Protocol library.
"""

from pathlib import Path
from typing import Optional


def extract_file_name(file_path: Path) -> str:
    """
    Extract a clean name from a file path.
    
    Args:
        file_path: Path object
        
    Returns:
        Clean file name without extension
    """
    return file_path.stem.replace('_', ' ').replace('-', ' ').title()


def generate_description(instructor_name: str, file_path: Optional[Path] = None) -> str:
    """
    Generate a description based on instructor name and optional file path.
    
    Args:
        instructor_name: The instructor name
        file_path: Optional file path for additional context
        
    Returns:
        Generated description
    """
    if file_path:
        return f"Context from {instructor_name} (source: {file_path.name})"
    else:
        return f"Context from {instructor_name}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_file_extension(file_path: Path, allowed_extensions: list = None) -> bool:
    """
    Validate that a file has an allowed extension.
    
    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed extensions (with dots)
        
    Returns:
        True if valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ['.txt', '.md']
    
    return file_path.suffix.lower() in allowed_extensions


def format_context_summary(instructor_name: str, description: str, content_preview: str) -> str:
    """
    Format a nice summary of a context.
    
    Args:
        instructor_name: Name of the instructor
        description: Context description
        content_preview: Preview of the content
        
    Returns:
        Formatted summary string
    """
    return f"""Instructor: {instructor_name}
Description: {description}
Preview: {content_preview}"""


def count_tokens_approximate(text: str) -> int:
    """
    Approximate token count for OpenAI models.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Approximate token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4