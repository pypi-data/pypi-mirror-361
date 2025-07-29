"""
AgentDS Python Client

Official Python client for AgentDS-Bench platform.
Provides seamless integration for benchmarking AI agent capabilities in data science tasks.
"""

__version__ = "1.2.2"
__author__ = "AgentDS Team"
__email__ = "contact@agentds.org"
__license__ = "MIT"

from .client import BenchmarkClient
from .task import Task
from .auth import authenticate, get_auth_info, get_auth_headers
from .config import API_BASE_URL
from .exceptions import (
    AgentDSError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
    DatasetError,
    TaskError,
    ConfigurationError,
)

__all__ = [
    "BenchmarkClient",
    "Task", 
    "authenticate",
    "get_auth_info",
    "get_auth_headers",
    "API_BASE_URL",
    "AgentDSError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "NetworkError",
    "DatasetError",
    "TaskError",
    "ConfigurationError",
] 