"""
Custom exceptions for AgentDS Python client.
"""


class AgentDSError(Exception):
    """Base exception for all AgentDS-related errors."""
    pass


class AuthenticationError(AgentDSError):
    """Raised when authentication fails."""
    pass


class APIError(AgentDSError):
    """Raised when API requests fail."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationError(AgentDSError):
    """Raised when response validation fails."""
    pass


class NetworkError(AgentDSError):
    """Raised when network requests fail."""
    pass


class DatasetError(AgentDSError):
    """Raised when dataset operations fail."""
    pass


class TaskError(AgentDSError):
    """Raised when task operations fail."""
    pass


class ConfigurationError(AgentDSError):
    """Raised when configuration is invalid."""
    pass 