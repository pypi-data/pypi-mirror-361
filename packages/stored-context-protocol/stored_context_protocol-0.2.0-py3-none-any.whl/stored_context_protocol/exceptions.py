"""Custom exceptions for Stored Context Protocol."""


class StoredContextProtocolError(Exception):
    """Base exception for Stored Context Protocol errors."""
    pass


class ContextNotFoundError(StoredContextProtocolError):
    """Raised when a context cannot be found."""
    pass


class InvalidFileFormatError(StoredContextProtocolError):
    """Raised when file format is not supported."""
    pass


class OpenAIError(StoredContextProtocolError):
    """Raised when OpenAI API operations fail."""
    pass