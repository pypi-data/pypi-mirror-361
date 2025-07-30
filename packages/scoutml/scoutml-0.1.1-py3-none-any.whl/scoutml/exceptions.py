"""Custom exceptions for ScoutML client."""


class ScoutMLError(Exception):
    """Base exception for ScoutML client errors."""
    pass


class AuthenticationError(ScoutMLError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ScoutMLError):
    """Raised when a resource is not found."""
    pass


class RateLimitError(ScoutMLError):
    """Raised when rate limit is exceeded."""
    pass


class ServerError(ScoutMLError):
    """Raised when server returns an error."""
    pass


class ValidationError(ScoutMLError):
    """Raised when input validation fails."""
    pass