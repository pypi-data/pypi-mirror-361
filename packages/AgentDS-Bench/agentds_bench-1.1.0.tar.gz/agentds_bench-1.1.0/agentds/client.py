"""
BenchmarkClient for interacting with the AgentDS-Bench platform.
"""

import json
import os
import time
from datetime import datetime

from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests

from .auth import authenticate, get_auth_headers, get_auth_info
from .config import API_BASE_URL, DEFAULT_TIMEOUT
from .exceptions import (
    APIError,
    AuthenticationError,
    DatasetError,
    NetworkError,
    TaskError,
    ValidationError,
)
from .task import Task
from .utils.validators import validate_csv_response


class BenchmarkClient:
    """
    Client for interacting with the AgentDS-Bench platform.
    
    This client provides methods to authenticate, retrieve tasks, and submit responses.
    Datasets are expected to be available directly in the user's environment.
    """
    
    TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".agentds_token")
    DATA_DIR = os.path.join(os.getcwd(), "agentDS_data")
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        team_name: Optional[str] = None, 
        dev_mode: bool = False
    ):
        """
        Initialize a new BenchmarkClient.
        
        If api_key and team_name are provided, the client will attempt to authenticate.
        Otherwise, it will try to load credentials from environment variables or the token file.
        
        Args:
            api_key: API key for authentication
            team_name: Team name for identification
            dev_mode: If True, enables development mode with simulated responses for offline testing
        """
        self.api_key = api_key
        self.team_name = team_name
        self.is_authenticated = False
        self.current_domain: Optional[str] = None
        self.current_task_number: Optional[int] = None
        self.current_task_test_size: Optional[int] = None
        self.dev_mode = dev_mode
        
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)
        
        if dev_mode and api_key and team_name:
            # In dev mode, skip authentication and assume success
            self.is_authenticated = True
        elif api_key and team_name:
            self.authenticate()
        else:
            loaded_api_key, loaded_team_name = get_auth_info()
            if loaded_api_key and loaded_team_name:
                self.api_key = loaded_api_key
                self.team_name = loaded_team_name
                if dev_mode:
                    self.is_authenticated = True
                else:
                    self.verify_auth()
            else:
                self._load_token()


    def _save_token(self) -> None:
        """Save authentication token to file with timestamp."""
        if self.api_key and self.team_name and self.is_authenticated:
            try:
                with open(self.TOKEN_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        'api_key': self.api_key,
                        'team_name': self.team_name,
                        'timestamp': datetime.now().timestamp()
                    }, f, indent=2)
            except (IOError, OSError):
                pass
    
    def _load_token(self) -> bool:
        """Load authentication token from file if it exists."""
        if os.path.exists(self.TOKEN_FILE):
            try:
                with open(self.TOKEN_FILE, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    
                    if datetime.now().timestamp() - token_data.get('timestamp', 0) < 7 * 24 * 3600:
                        if 'teams' in token_data:
                            teams_dict = token_data.get('teams', {})
                            if teams_dict:
                                team_name = next(iter(teams_dict), None)
                                if team_name:
                                    self.team_name = team_name
                                    self.api_key = teams_dict[team_name]
                        else:
                            self.api_key = token_data.get('api_key')
                            self.team_name = token_data.get('team_name')
                        
                        if self.api_key and self.team_name:
                            return self.verify_auth()
            except (json.JSONDecodeError, IOError, OSError):
                pass
        return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with the AgentDS-Bench platform.
        
        Returns:
            bool: True if authentication was successful, False otherwise
            
        Raises:
            AuthenticationError: If credentials are missing or invalid
        """
        if not self.api_key or not self.team_name:
            raise AuthenticationError("API key and team name are required for authentication.")
        
        self.is_authenticated = authenticate(self.api_key, self.team_name)
        
        if self.is_authenticated:
            self._save_token()
        else:
            raise AuthenticationError("Authentication failed with provided credentials.")
            
        return self.is_authenticated
    
    def verify_auth(self) -> bool:
        """
        Verify that the client is authenticated.
        
        Returns:
            bool: True if the client is authenticated, False otherwise
        """
        if self.is_authenticated:
            return True
            
        if not self.api_key or not self.team_name:
            return False
            
        try:
            headers = get_auth_headers()
            response = requests.get(
                f"{API_BASE_URL}/auth/verify",
                headers=headers,
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                self.is_authenticated = True
                return True
            elif response.status_code == 400:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", "")
                    if "Team ID" in err_msg:
                        self.is_authenticated = True
                        return True
                except (ValueError, KeyError):
                    pass
                
            self.is_authenticated = False
            return False
        except requests.RequestException:
            return False
    
    def start_competition(self) -> bool:
        """
        Start the competition for this team.
        
        Returns:
            bool: True if the competition was started successfully, False otherwise
            
        Raises:
            AuthenticationError: If client is not authenticated
            APIError: If the API request fails
        """
        if not self.verify_auth():
            raise AuthenticationError("Authentication required to start competition.")
            
        try:
            response = requests.post(
                f"{API_BASE_URL}/competition/start",
                headers=get_auth_headers(),
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                return True
            else:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", "Unknown error")
                except (ValueError, KeyError):
                    err_msg = f"HTTP {response.status_code}"
                raise APIError(f"Failed to start competition: {err_msg}", response.status_code)
        except requests.RequestException as e:
            raise NetworkError(f"Error starting competition: {e}")
    
    def get_domains(self) -> List[str]:
        """
        Get the list of available domains.
        
        Returns:
            List[str]: List of domain names
        """
        if not self.verify_auth():
            return []
            
        try:
            response = requests.get(
                f"{API_BASE_URL}/competition/domains",
                headers=get_auth_headers()
            )
            
            if response.status_code == 200:
                domains = response.json().get("domains", [])
                return domains
            else:
                err_msg = response.json().get("error", "Unknown error")
                print(f"Failed to get domains: {err_msg}")
                return []
        except requests.RequestException as e:
            print(f"Error getting domains: {e}")
            return []
    
    def get_next_task(self, domain: str) -> Optional[Task]:
        """
        Get the next task for a specific domain.
        
        Args:
            domain: The domain to get the next task for
            
        Returns:
            Task: The next task, or None if no task is available
        """
        if not self.verify_auth():
            return None
        
        # Update the current domain
        self.current_domain = domain
            
        try:
            response = requests.get(
                f"{API_BASE_URL}/competition/task/{domain}",
                headers=get_auth_headers()
            )
            
            if response.status_code == 200:
                task_data = response.json()
                
                # Check if we got a proper task response
                task_info = task_data.get("task")
                if not task_info:
                    print(f"No task data found in response for domain {domain}")
                    return None
                
                # Create a Task object from the response
                task = Task(
                    task_number=task_info.get("task_number"),
                    domain=task_info.get("domain", domain),
                    category=task_info.get("category", ""),
                    data=task_info.get("data"),
                    instructions=task_info.get("task_instruction", ""),
                    side_info=task_info.get("side_information_list", {}),
                    response_format=task_info.get("response_format", {}),
                    test_size=task_data.get("test_size", 0),
                    client=self
                )
                
                # Save the current task number and test size
                self.current_task_number = task.task_number
                self.current_task_test_size = task.test_size
                
                # Save dataset to local file if available
                if task.data and isinstance(task.data, str):
                    # Create domain directory if it doesn't exist
                    domain_dir = os.path.join(self.DATA_DIR, domain)
                    if not os.path.exists(domain_dir):
                        os.makedirs(domain_dir)
                    
                    # Create the dataset file path
                    file_name = f"task_{task.task_number}_data.csv"
                    dataset_path = os.path.join(domain_dir, file_name)
                    
                    # Save the data to file
                    with open(dataset_path, "w") as f:
                        f.write(task.data)
                    
                    # Add the path to the task object for user convenience
                    task.dataset_path = dataset_path
                    print(f"Dataset saved to {dataset_path}")
                
                return task
            elif response.status_code == 404:
                # No task available in this domain
                print(f"No task available for domain {domain}")
                return None
            else:
                err_msg = "Unknown error"
                try:
                    err_msg = response.json().get("error", "Unknown error")
                except:
                    err_msg = f"HTTP error {response.status_code}"
                print(f"Failed to get next task: {err_msg}")
                return None
        except requests.RequestException as e:
            print(f"Error getting next task: {e}")
            return None
    
    def submit_response(self, domain: str, task_number: int, response: Any) -> bool:
        """
        Submit a response for a specific task.
        
        Args:
            domain: The domain of the task
            task_number: The task number within the domain
            response: The response data to submit
            
        Returns:
            bool: True if the response was submitted successfully, False otherwise
        """
        if not self.verify_auth():
            return False
            
        try:
            # Prepare the payload
            payload = {
                "response": response
            }
            
            response_obj = requests.post(
                f"{API_BASE_URL}/competition/submit/{domain}/{task_number}",
                headers=get_auth_headers(),
                json=payload
            )
            
            if response_obj.status_code == 200:
                result = response_obj.json()
                score = result.get('score', 'N/A')
                print(f"Response submitted successfully. Score: {score}")
                
                # Check if domain is completed
                if result.get("domain_completed", False):
                    print(f"Congratulations! Domain '{domain}' is completed.")
                
                return True
            else:
                err_msg = response_obj.json().get("error", "Unknown error")
                print(f"Failed to submit response: {err_msg}")
                return False
        except requests.RequestException as e:
            print(f"Error submitting response: {e}")
            return False
    
    def submit_prediction(self, domain_name: str, task_number: int, predictions_file: str) -> Dict[str, Any]:
        """
        Submit predictions for evaluation.
        
        This method validates the prediction file format and submits it to the 
        AgentDS-Bench evaluation system for scoring against ground truth data.
        
        Args:
            domain_name: Name of the domain (e.g., "Insurance", "Commerce")
            task_number: Challenge number within the domain (1, 2, 3, etc.)
            predictions_file: Path to CSV file containing predictions
            
        Returns:
            Dict containing evaluation results:
            {
                "success": bool,
                "score": float,
                "metric_name": str,
                "validation_passed": bool,
                "details": {
                    "expected_format": str,
                    "actual_rows": int,
                    "expected_rows": int,
                    "validation_errors": [str]
                }
            }
            
        Raises:
            ValueError: If parameters are invalid or file cannot be processed
            requests.RequestException: If API communication fails
            
        Example:
            >>> client = BenchmarkClient()
            >>> result = client.submit_prediction("Insurance", 1, "my_predictions.csv")
            >>> print(f"Score: {result['score']}, Metric: {result['metric_name']}")
        """
        
        # 1. Input parameter validation
        if not isinstance(domain_name, str) or not domain_name.strip():
            raise ValueError("domain_name must be a non-empty string")
            
        if not isinstance(task_number, int) or task_number < 1:
            raise ValueError("task_number must be a positive integer")
            
        if not isinstance(predictions_file, str) or not predictions_file.strip():
            raise ValueError("predictions_file must be a non-empty string")
        
        # 2. Authentication check
        if not self.verify_auth():
            return {
                "success": False,
                "score": 0.0,
                "metric_name": "N/A",
                "validation_passed": False,
                "details": {
                    "expected_format": "Unknown",
                    "actual_rows": 0,
                    "expected_rows": 0,
                    "validation_errors": ["Authentication failed. Please authenticate first."]
                }
            }
        
        # 3. File existence and readability validation
        if not os.path.exists(predictions_file):
            raise ValueError(f"Predictions file does not exist: {predictions_file}")
            
        if not os.path.isfile(predictions_file):
            raise ValueError(f"Path is not a file: {predictions_file}")
            
        try:
            # Test file readability
            with open(predictions_file, 'r', encoding='utf-8') as f:
                # Try to read first few characters to ensure file is readable
                f.read(100)
        except (IOError, OSError, UnicodeDecodeError) as e:
            raise ValueError(f"Cannot read predictions file: {str(e)}")
        
        # 4. CSV content reading and basic validation
        try:
            predictions_df = pd.read_csv(predictions_file)
            
            # Basic CSV structure validation
            if predictions_df.empty:
                raise ValueError("Predictions file is empty")
                
            if predictions_df.shape[1] < 2:
                raise ValueError(f"CSV must have at least 2 columns, found {predictions_df.shape[1]}")
                
            # Check for missing values
            if predictions_df.isna().any().any():
                raise ValueError("CSV contains missing values")
                
            # Convert DataFrame to CSV string for API submission
            predictions_csv_content = predictions_df.to_csv(index=False)
            
        except pd.errors.EmptyDataError:
            raise ValueError("Predictions file is empty or has no data")
        except pd.errors.ParserError as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}")
        
        # 5. Development mode handling
        if self.dev_mode:
            print("DEV MODE: Simulating prediction submission")
            return {
                "success": True,
                "score": 0.85,
                "metric_name": "Macro-F1",
                "validation_passed": True,
                "details": {
                    "expected_format": "ID,Prediction",
                    "actual_rows": len(predictions_df),
                    "expected_rows": len(predictions_df),
                    "validation_errors": []
                }
            }
        
        # 6. API submission
        try:
            # Prepare payload for API
            payload = {
                "domain_name": domain_name.strip(),
                "task_number": task_number,
                "predictions_csv": predictions_csv_content
            }
            
            # Make API request to the evaluation endpoint
            response = requests.post(
                f"{API_BASE_URL}/submit",  # Note: Using /submit as per instructions
                headers=get_auth_headers(),
                json=payload,
                timeout=30  # 30 second timeout for evaluation
            )
            
            # 7. Response handling
            if response.status_code == 200:
                result = response.json()
                
                # Ensure response has expected structure
                evaluation_result = {
                    "success": result.get("success", False),
                    "score": float(result.get("score", 0.0)),
                    "metric_name": result.get("metric_name", "Unknown"),
                    "validation_passed": result.get("validation_passed", False),
                    "details": result.get("details", {
                        "expected_format": "Unknown",
                        "actual_rows": len(predictions_df),
                        "expected_rows": 0,
                        "validation_errors": ["Unknown response format"]
                    })
                }
                
                # Print user-friendly feedback
                if evaluation_result["success"]:
                    print(f"✅ Prediction submitted successfully!")
                    print(f"📊 Score: {evaluation_result['score']:.4f} ({evaluation_result['metric_name']})")
                    if evaluation_result["validation_passed"]:
                        print(f"✅ Validation passed")
                    else:
                        print(f"⚠️  Validation issues detected")
                else:
                    print(f"❌ Submission failed")
                    if not evaluation_result["validation_passed"]:
                        print(f"❌ Validation failed")
                        errors = evaluation_result["details"].get("validation_errors", [])
                        for error in errors[:5]:  # Show first 5 errors
                            print(f"   • {error}")
                
                return evaluation_result
                
            elif response.status_code == 404:
                return {
                    "success": False,
                    "score": 0.0,
                    "metric_name": "N/A",
                    "validation_passed": False,
                    "details": {
                        "expected_format": "Unknown",
                        "actual_rows": len(predictions_df),
                        "expected_rows": 0,
                        "validation_errors": [f"Task not found: {domain_name}, task {task_number}"]
                    }
                }
                
            elif response.status_code == 400:
                # Bad request - likely validation error
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Bad request")
                    return {
                        "success": False,
                        "score": 0.0,
                        "metric_name": "N/A", 
                        "validation_passed": False,
                        "details": {
                            "expected_format": "Unknown",
                            "actual_rows": len(predictions_df),
                            "expected_rows": 0,
                            "validation_errors": [error_msg]
                        }
                    }
                except:
                    return {
                        "success": False,
                        "score": 0.0,
                        "metric_name": "N/A",
                        "validation_passed": False,
                        "details": {
                            "expected_format": "Unknown",
                            "actual_rows": len(predictions_df),
                            "expected_rows": 0,
                            "validation_errors": [f"Bad request (HTTP {response.status_code})"]
                        }
                    }
                    
            else:
                # Other HTTP errors
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}"
                    
                return {
                    "success": False,
                    "score": 0.0,
                    "metric_name": "N/A",
                    "validation_passed": False,
                    "details": {
                        "expected_format": "Unknown",
                        "actual_rows": len(predictions_df),
                        "expected_rows": 0,
                        "validation_errors": [f"Server error: {error_msg}"]
                    }
                }
                
        except requests.Timeout:
            raise requests.RequestException("Request timeout - evaluation took too long")
        except requests.ConnectionError as e:
            raise requests.RequestException(f"Connection error: {str(e)}")
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")
        except Exception as e:
            # Catch any other unexpected errors
            return {
                "success": False,
                "score": 0.0,
                "metric_name": "N/A",
                "validation_passed": False,
                "details": {
                    "expected_format": "Unknown",
                    "actual_rows": len(predictions_df) if 'predictions_df' in locals() else 0,
                    "expected_rows": 0,
                    "validation_errors": [f"Unexpected error: {str(e)}"]
                }
            }
    
    def get_status(self) -> Dict:
        """
        Get the current status of the competition for this team.
        
        Returns:
            Dict: Detailed status including domain completion information
        """
        if not self.verify_auth():
            return {"status": "inactive"}
            
        try:
            response = requests.get(
                f"{API_BASE_URL}/competition/status",
                headers=get_auth_headers()
            )
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Format as a nice table for display if domains info is available
                if "domains" in status_data:
                    domains_data = []
                    for domain in status_data["domains"]:
                        domains_data.append({
                            "Domain": domain.get("name", "Unknown"),
                            "Completed Tasks": domain.get("completed_tasks", 0),
                            "Total Tasks": domain.get("total_tasks", 0),
                            "Status": "Completed" if domain.get("completed", False) else "In Progress",
                            "Best Score": domain.get("best_score", "N/A"),
                            "Start Time": domain.get("start_time", "Not Started"),
                            "Completion Time": domain.get("completion_time", "Not Completed")
                        })
                    
                    status_df = pd.DataFrame(domains_data)
                    status_data["formatted_table"] = status_df.to_string(index=False)
                    status_data["completed_domains"] = [d.get("name") for d in status_data["domains"] if d.get("completed", False)]
                    status_data["incomplete_domains"] = [d.get("name") for d in status_data["domains"] if not d.get("completed", False)]
                
                return status_data
            else:
                err_msg = response.json().get("error", "Unknown error")
                print(f"Failed to get status: {err_msg}")
                
                # In dev mode, return a fallback status
                if self.dev_mode:
                    print("DEV MODE: Returning fallback status")
                    return {
                        "status": "active",
                        "team_name": self.team_name,
                        "domain_progress": {},
                        "overall_progress": 0
                    }
                return {"status": "error", "message": err_msg}
        except requests.RequestException as e:
            print(f"Error getting status: {e}")
            
            # In dev mode, return a fallback status
            if self.dev_mode:
                print("DEV MODE: Returning fallback status")
                return {
                    "status": "active",
                    "team_name": self.team_name,
                    "domain_progress": {},
                    "overall_progress": 0
                }
            return {"status": "error", "message": str(e)}
            
    @staticmethod
    def list_stored_teams() -> List[str]:
        """
        List all teams that have been authenticated and stored.
        
        Returns:
            List[str]: List of team names
        """
        from .auth import load_teams_dict
        teams_dict = load_teams_dict()
        return list(teams_dict.keys())
        
    @staticmethod
    def switch_team(team_name: str) -> bool:
        """
        Switch to using a different team for API calls.
        
        Args:
            team_name: The name of the team to switch to
            
        Returns:
            bool: True if the team was found and switched to, False otherwise
        """
        from .auth import select_team
        return select_team(team_name)
