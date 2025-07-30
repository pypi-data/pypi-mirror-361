"""
Stored Context Protocol Library
A library for managing and selecting contextual information based on instructor names.
"""

from .core.context_manager import ContextManager
from .core.models import Context
from .exceptions import (
    StoredContextProtocolError,
    ContextNotFoundError,
    InvalidFileFormatError,
    OpenAIError
)

__version__ = "1.0.0"
__all__ = [
    "ContextManager",
    "Context",
    "StoredContextProtocolError",
    "ContextNotFoundError",
    "InvalidFileFormatError",
    "OpenAIError"
]