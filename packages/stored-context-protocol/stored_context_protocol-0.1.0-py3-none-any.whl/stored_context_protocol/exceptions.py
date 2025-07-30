"""
Custom exceptions for the Stored Context Protocol library.
"""


class SCPError(Exception):
    """Base exception for all SCP errors."""
    pass


class ContextNotFoundError(SCPError):
    """Raised when a requested context is not found."""
    pass


class APIError(SCPError):
    """Raised when there's an error with the OpenAI API."""
    pass


class StorageError(SCPError):
    """Raised when there's an error with context storage."""
    pass


class ValidationError(SCPError):
    """Raised when input validation fails."""
    pass