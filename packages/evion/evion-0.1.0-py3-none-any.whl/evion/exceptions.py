"""
Custom exceptions for the Evion library.
"""


class EvionError(Exception):
    """Base exception for all Evion-related errors."""
    pass


class AuthenticationError(EvionError):
    """Raised when API key authentication fails."""
    pass


class APIError(EvionError):
    """Raised when API requests fail."""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(EvionError):
    """Raised when input validation fails."""
    pass


class NetworkError(EvionError):
    """Raised when network requests fail."""
    pass


class FileError(EvionError):
    """Raised when file operations fail."""
    pass 