"""
Stored Context Protocol (SCP) - A Python library for managing and retrieving contextual information
using OpenAI's function calling capabilities.
"""

from .core import StoredContextProtocol
from .models import Context, InstructorInfo
from .exceptions import SCPError, ContextNotFoundError, APIError

# Alias for easier usage
ContextManager = StoredContextProtocol

__version__ = "0.1.0"
__all__ = [
    "StoredContextProtocol",
    "ContextManager",
    "Context",
    "InstructorInfo",
    "SCPError",
    "ContextNotFoundError",
    "APIError"
]