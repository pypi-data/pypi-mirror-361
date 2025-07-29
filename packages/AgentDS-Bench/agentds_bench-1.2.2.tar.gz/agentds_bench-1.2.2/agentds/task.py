"""
Task representation for the AgentDS-Bench platform.
"""

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from .client import BenchmarkClient


class Task:
    """
    Represents a benchmarking task in the AgentDS-Bench platform.
    
    A task contains the data, instructions, and metadata needed for an agent to complete
    a specific data science challenge.
    """
    
    def __init__(
        self, 
        task_number: int, 
        domain: str, 
        category: str, 
        data: Any, 
        instructions: str, 
        side_info: Optional[Any] = None, 
        response_format: Optional[Dict] = None,
        test_size: Optional[int] = None,
        client: Optional['BenchmarkClient'] = None
    ):
        """
        Initialize a new Task instance.
        
        Args:
            task_number: Task number within the domain
            domain: The domain or field this task belongs to
            category: The scaling category (Fidelity, Volume, Noise, Complexity)
            data: The primary data for the task
            instructions: Task instructions and requirements
            side_info: Additional information or context
            response_format: Expected format for the response
            test_size: Expected number of rows in the response CSV
            client: Reference to the BenchmarkClient that created this task
        """
        self.task_number = task_number
        self.domain = domain
        self.category = category
        self.data = data
        self.instructions = instructions
        self.side_info = side_info or {}
        self.response_format = response_format or {}
        self.test_size = test_size
        self._client = client
        self.dataset_path: Optional[str] = None
    
    def get_data(self) -> Any:
        """
        Get the primary data for this task.
        
        Returns:
            The task data
        """
        return self.data
    
    def get_instructions(self) -> str:
        """
        Get the instructions for this task.
        
        Returns:
            Task instructions as a string
        """
        return self.instructions
    
    def get_side_info(self) -> Any:
        """
        Get additional information or context for this task.
        
        Returns:
            Additional information
        """
        return self.side_info
    
    def get_response_format(self) -> Dict:
        """
        Get the expected format for the response.
        
        Returns:
            A dictionary describing the expected response format
        """
        return self.response_format
    
    def get_test_size(self) -> Optional[int]:
        """
        Get the expected number of rows in the response CSV.
        
        Returns:
            Expected number of rows or None if not specified
        """
        return self.test_size
    
    def validate_response(self, response: Any) -> bool:
        """
        Validate that a response matches the expected format.
        
        Args:
            response: The response to validate
            
        Returns:
            True if the response is valid, False otherwise
        """
        if not self.response_format:
            return True
            
        try:
            if isinstance(self.response_format, dict) and isinstance(response, dict):
                for key in self.response_format:
                    if key not in response:
                        return False
                return True
            else:
                return isinstance(response, type(self.response_format))
        except Exception:
            return False

    def load_dataset(self) -> Tuple['pd.DataFrame', 'pd.DataFrame', 'pd.DataFrame']:
        """
        Load the dataset for this task's domain directly from the platform database.
        
        This is a convenience method that uses the client to load the dataset
        for the domain this task belongs to.
        
        Returns:
            Tuple of (train_df, test_df, sample_submission_df) as pandas DataFrames
            
        Raises:
            RuntimeError: If no client is available to load the dataset
            ValueError: If domain is not found or data is missing
            Exception: If database connection fails
        """
        if not self._client:
            raise RuntimeError(
                "Cannot load dataset: no client available. "
                "Use client.load_dataset(domain_name) instead, or get this task "
                "from a BenchmarkClient instance."
            )
        
        return self._client.load_dataset(self.domain)

    def __repr__(self) -> str:
        """Return string representation of the task."""
        return f"Task(task_number={self.task_number}, domain='{self.domain}', category='{self.category}')"

    def __str__(self) -> str:
        """Return human-readable string representation of the task."""
        return f"Task #{self.task_number} in {self.domain} domain ({self.category})" 