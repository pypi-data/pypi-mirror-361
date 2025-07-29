"""
Validation utilities for AgentDS Python client.
"""

import pandas as pd
from typing import Any, Dict, List, Tuple, Union
from ..exceptions import ValidationError


def validate_csv_response(file_path: str, expected_rows: int = 0) -> Tuple[bool, str]:
    """
    Validate a CSV response file to ensure it has correct format.
    
    Args:
        file_path: Path to the CSV file to validate
        expected_rows: Expected number of rows (excluding header), 0 means skip validation
        
    Returns:
        Tuple containing validation result and error message if failed
    """
    try:
        df = pd.read_csv(file_path)
        
        if df.empty:
            return False, "CSV file is empty"
        
        if df.shape[1] != 2:
            return False, f"CSV must have exactly 2 columns, found {df.shape[1]}"
        
        if expected_rows > 0:
            actual_rows = df.shape[0]
            if actual_rows != expected_rows:
                return False, f"CSV must have exactly {expected_rows} data rows, found {actual_rows}"
        
        if df.isna().any().any():
            return False, "CSV contains missing values"
            
        return True, ""
        
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError:
        return False, "Invalid CSV format"
    except Exception as e:
        return False, f"Error validating CSV: {str(e)}"


def validate_api_response(response_data: Dict[str, Any]) -> bool:
    """
    Validate API response structure.
    
    Args:
        response_data: Response data from API
        
    Returns:
        True if response is valid, False otherwise
    """
    if not isinstance(response_data, dict):
        return False
    
    required_fields = ["success"]
    return all(field in response_data for field in required_fields)


def validate_task_response(response: Any, expected_format: Dict[str, Any] = None) -> bool:
    """
    Validate a task response against expected format.
    
    Args:
        response: The response to validate
        expected_format: Expected format specification
        
    Returns:
        True if response is valid, False otherwise
    """
    if expected_format is None:
        return True
    
    try:
        if isinstance(expected_format, dict) and isinstance(response, dict):
            for key in expected_format:
                if key not in response:
                    return False
            return True
        else:
            return isinstance(response, type(expected_format))
    except Exception:
        return False


def validate_credentials(api_key: str, team_name: str) -> None:
    """
    Validate API credentials format.
    
    Args:
        api_key: API key to validate
        team_name: Team name to validate
        
    Raises:
        ValidationError: If credentials are invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key must be a non-empty string")
    
    if not team_name or not isinstance(team_name, str):
        raise ValidationError("Team name must be a non-empty string")
    
    if len(api_key.strip()) < 10:
        raise ValidationError("API key appears to be too short")
    
    if len(team_name.strip()) < 2:
        raise ValidationError("Team name appears to be too short")


def validate_domain_name(domain_name: str) -> None:
    """
    Validate domain name format.
    
    Args:
        domain_name: Domain name to validate
        
    Raises:
        ValidationError: If domain name is invalid
    """
    if not domain_name or not isinstance(domain_name, str):
        raise ValidationError("Domain name must be a non-empty string")
    
    if not domain_name.strip():
        raise ValidationError("Domain name cannot be empty or whitespace only") 