"""
Basic example demonstrating AgentDS Python client usage.

This example shows how to:
- Authenticate with the platform
- Start a competition
- Get available domains
- Retrieve and process tasks
- Submit responses
"""

import os
from typing import Any, Dict

from agentds import BenchmarkClient
from agentds.exceptions import AuthenticationError, APIError


def simple_agent(task) -> Dict[str, Any]:
    """
    A simple agent implementation for demonstration purposes.
    
    In a real implementation, this would contain your data science logic
    to analyze the task data and generate appropriate responses.
    
    Args:
        task: The task to process
        
    Returns:
        A response dictionary
    """
    data = task.get_data()
    instructions = task.get_instructions()
    
    # For demonstration, return a simple response
    # In practice, you would implement your analysis here
    return {
        "result": "processed",
        "confidence": 0.85,
        "method": "basic_analysis"
    }


def main():
    """Demonstrate basic AgentDS client usage."""
    try:
        # Initialize client - will use environment variables or saved credentials
        client = BenchmarkClient()
        
        # Start the competition
        client.start_competition()
        
        # Get available domains
        domains = client.get_domains()
        print(f"Available domains: {domains}")
        
        # Process tasks from the first available domain
        if domains:
            domain = domains[0]
            print(f"Processing domain: {domain}")
            
            # Get a task
            task = client.get_next_task(domain)
            if task:
                print(f"Retrieved task #{task.task_number} from {task.domain}")
                
                # Process the task
                response = simple_agent(task)
                
                # Validate and submit
                if task.validate_response(response):
                    success = client.submit_response(domain, task.task_number, response)
                    if success:
                        print("Response submitted successfully!")
                    else:
                        print("Failed to submit response")
                else:
                    print("Response validation failed")
            else:
                print(f"No tasks available for domain {domain}")
        else:
            print("No domains available")
            
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
        print("Please set AGENTDS_API_KEY and AGENTDS_TEAM_NAME environment variables")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main() 