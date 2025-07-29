"""
Authentication module for AgentDS Python client.

Handles API key authentication, credential storage, and team management.
"""

import os
import json
import requests
from typing import Optional, Tuple, Dict, List
from .config import API_BASE_URL, TOKEN_FILE, DEFAULT_TIMEOUT


def authenticate(api_key: str, team_name: str) -> bool:
    """
    Authenticate a team with the AgentDS-Bench platform using API key.
    
    Args:
        api_key: The API key generated for the team
        team_name: The name of the team
    
    Returns:
        bool: True if authentication was successful, False otherwise
    """
    os.environ["AGENTDS_API_KEY"] = api_key
    os.environ["AGENTDS_TEAM_NAME"] = team_name
    
    if verify_api_key(api_key, team_name):
        teams_dict = load_teams_dict()
        teams_dict[team_name] = api_key
        save_teams_dict(teams_dict)
        return True
    
    return False


def verify_api_key(api_key: str, team_name: str) -> bool:
    """
    Verify the API key with the server.
    
    Args:
        api_key: The API key to verify
        team_name: The name of the team associated with the API key
    
    Returns:
        bool: True if verification was successful, False otherwise
    """
    headers = {
        "X-API-Key": api_key,
        "X-Team-Name": team_name,
        "X-Team-ID": "placeholder"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify",
            headers=headers,
            timeout=DEFAULT_TIMEOUT
        )
        
        if response.status_code == 200:
            return True
        
        try:
            err_data = response.json()
            err_msg = err_data.get("error", "Unknown error")
            if err_msg == "Team ID is required":
                return True
        except (ValueError, KeyError):
            pass
            
        return False
        
    except requests.RequestException:
        return False


def load_teams_dict() -> Dict[str, str]:
    """
    Load the dictionary of team names and API keys from the token file.
    
    Returns:
        Dict[str, str]: Dictionary with team names as keys and API keys as values
    """
    teams_dict = {}
    
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if isinstance(data, dict):
                    if "teams" in data:
                        teams_dict = data.get("teams", {})
                    elif "team_name" in data and "api_key" in data:
                        team_name = data.get("team_name")
                        api_key = data.get("api_key")
                        if team_name and api_key:
                            teams_dict[team_name] = api_key
        except (json.JSONDecodeError, IOError):
            pass
    
    return teams_dict


def save_teams_dict(teams_dict: Dict[str, str]) -> None:
    """
    Save the dictionary of team names and API keys to the token file.
    
    Args:
        teams_dict: Dictionary with team names as keys and API keys as values
    """
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"teams": teams_dict}, f, indent=2)
    except IOError:
        pass


def get_auth_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve the API key and team name from environment variables or token file.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the API key and team name,
        or (None, None) if not found.
    """
    api_key = os.getenv("AGENTDS_API_KEY")
    team_name = os.getenv("AGENTDS_TEAM_NAME")
    
    if api_key and team_name:
        return api_key, team_name
    
    teams_dict = load_teams_dict()
    if teams_dict:
        team_name = next(iter(teams_dict), None)
        if team_name:
            api_key = teams_dict[team_name]
            os.environ["AGENTDS_API_KEY"] = api_key
            os.environ["AGENTDS_TEAM_NAME"] = team_name
            return api_key, team_name
    
    return None, None


def get_auth_headers() -> Dict[str, str]:
    """
    Return the authentication headers for API requests.
    
    Returns:
        dict: Headers containing the API key and team name
    """
    api_key, team_name = get_auth_info()
    
    if not api_key or not team_name:
        return {}
    
    return {
        "X-API-Key": api_key,
        "X-Team-Name": team_name,
        "X-Team-ID": "placeholder"
    }


def list_teams() -> List[str]:
    """
    List all teams that the user has authenticated with.
    
    Returns:
        List[str]: List of team names
    """
    teams_dict = load_teams_dict()
    return list(teams_dict.keys())


def select_team(team_name: str) -> bool:
    """
    Select a specific team for the current session.
    
    Args:
        team_name: Name of the team to select
        
    Returns:
        bool: True if team was found and selected, False otherwise
    """
    teams_dict = load_teams_dict()
    
    if team_name in teams_dict:
        api_key = teams_dict[team_name]
        os.environ["AGENTDS_API_KEY"] = api_key
        os.environ["AGENTDS_TEAM_NAME"] = team_name
        return True
    
    return False
