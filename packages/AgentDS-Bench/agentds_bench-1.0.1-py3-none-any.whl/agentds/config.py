"""
Configuration settings for AgentDS Python client.
"""

import os
from typing import Optional

def get_api_base_url() -> str:
    """
    Get the API base URL from environment variables or use default.
    
    Returns:
        str: The API base URL
    """
    return os.getenv("AGENTDS_API_URL", "https://agentds.org/api")

def get_token_file_path() -> str:
    """
    Get the path to the token file.
    
    Returns:
        str: Path to the token file in user's home directory
    """
    return os.path.expanduser("~/.agentds_token")

# Public API
API_BASE_URL = get_api_base_url()
TOKEN_FILE = get_token_file_path()

# MongoDB configuration
def get_mongo_uri() -> str:
    """
    Get MongoDB URI from environment variables.
    
    Returns:
        str: MongoDB connection URI
        
    Raises:
        ValueError: If MONGO_URI environment variable is not set
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError(
            "MONGO_URI environment variable is required. "
            "Please set it to your MongoDB connection string."
        )
    return mongo_uri

def get_db_name() -> str:
    """
    Get database name from environment variables or use default.
    
    Returns:
        str: Database name
    """
    return os.getenv("AGENTDS_DB_NAME", "agentds")

# MongoDB settings
MONGO_URI = get_mongo_uri()
DB_NAME = get_db_name()

# Request configuration
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1.0
