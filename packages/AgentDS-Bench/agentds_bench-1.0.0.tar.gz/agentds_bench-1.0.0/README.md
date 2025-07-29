# AgentDS Python Client

[![PyPI version](https://badge.fury.io/py/agentds.svg)](https://badge.fury.io/py/agentds)
[![Python Support](https://img.shields.io/pypi/pyversions/agentds.svg)](https://pypi.org/project/agentds/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python client for [AgentDS-Bench](https://agentds.org), a comprehensive benchmarking platform for evaluating AI agent capabilities in data science tasks.

## Features

- **Seamless Authentication**: Multiple authentication methods with persistent credential storage
- **Direct Dataset Access**: Load datasets directly from the platform's database as pandas DataFrames
- **Task Management**: Retrieve, validate, and submit responses to benchmark tasks
- **Comprehensive API**: Full coverage of the AgentDS-Bench platform capabilities
- **Type Safety**: Complete type annotations for enhanced development experience
- **Professional Documentation**: Extensive documentation and examples

## Installation

Install the package from PyPI:

```bash
pip install agentds
```

For development or to access example dependencies:

```bash
pip install agentds[examples]
```

## Quick Start

### Authentication

Get your API credentials from the [AgentDS platform](https://agentds.org) and authenticate:

```python
from agentds import BenchmarkClient

# Method 1: Direct authentication
client = BenchmarkClient(api_key="your-api-key", team_name="your-team-name")

# Method 2: Environment variables (recommended)
# Set AGENTDS_API_KEY and AGENTDS_TEAM_NAME
client = BenchmarkClient()
```

### Basic Usage

```python
from agentds import BenchmarkClient

# Initialize client
client = BenchmarkClient()

# Start competition
client.start_competition()

# Get available domains
domains = client.get_domains()
print(f"Available domains: {domains}")

# Get next task
task = client.get_next_task("machine-learning")
if task:
    # Access task data
    data = task.get_data()
    instructions = task.get_instructions()
    
    # Your solution here
    response = {"prediction": 0.85, "confidence": 0.92}
    
    # Validate and submit
    if task.validate_response(response):
        client.submit_response(task.domain, task.task_number, response)
```

### Dataset Loading

Load datasets directly as pandas DataFrames:

```python
import pandas as pd
from agentds import BenchmarkClient

client = BenchmarkClient()

# Load complete dataset
train_df, test_df, sample_df = client.load_dataset("Wine-Quality")

print(f"Training data: {train_df.shape}")
print(f"Test data: {test_df.shape}")
print(train_df.head())
```

## Authentication Methods

### Environment Variables

Set these environment variables for automatic authentication:

```bash
export AGENTDS_API_KEY="your-api-key"
export AGENTDS_TEAM_NAME="your-team-name"
export AGENTDS_API_URL="https://api.agentds.org/api"  # optional
```

### Configuration File

Create a `.env` file in your project directory:

```env
AGENTDS_API_KEY=your-api-key
AGENTDS_TEAM_NAME=your-team-name
AGENTDS_API_URL=https://api.agentds.org/api
```

### Persistent Storage

Authentication credentials are automatically saved to `~/.agentds_token` for future sessions.

## API Reference

### BenchmarkClient

Main client class for interacting with the AgentDS platform.

#### Methods

- `authenticate() -> bool`: Authenticate with the platform
- `start_competition() -> bool`: Start the competition
- `get_domains() -> List[str]`: Get available domains
- `get_next_task(domain: str) -> Optional[Task]`: Get next task for domain
- `submit_response(domain: str, task_number: int, response: Any) -> bool`: Submit task response
- `load_dataset(domain_name: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`: Load dataset
- `get_status() -> Dict`: Get competition status

### Task

Represents a benchmark task.

#### Properties

- `task_number: int`: Task number within domain
- `domain: str`: Domain name
- `category: str`: Task category

#### Methods

- `get_data() -> Any`: Get task data
- `get_instructions() -> str`: Get task instructions
- `get_side_info() -> Any`: Get additional information
- `validate_response(response: Any) -> bool`: Validate response format
- `load_dataset() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`: Load associated dataset

## Examples

### Complete Agent Example

```python
from agentds import BenchmarkClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def intelligent_agent():
    client = BenchmarkClient()
    client.start_competition()
    
    domains = client.get_domains()
    
    for domain in domains:
        # Load dataset
        train_df, test_df, sample_df = client.load_dataset(domain)
        
        # Get task
        task = client.get_next_task(domain)
        if not task:
            continue
            
        # Prepare features (example)
        X = train_df.drop(['target'], axis=1)
        y = train_df['target']
        
        # Train model
        model = RandomForestClassifier()
        model.fit(X, y)
        
        # Make predictions
        predictions = model.predict(test_df)
        
        # Format response
        response = {
            "predictions": predictions.tolist(),
            "model": "RandomForestClassifier",
            "confidence": float(model.score(X, y))
        }
        
        # Submit
        if task.validate_response(response):
            client.submit_response(domain, task.task_number, response)

if __name__ == "__main__":
    intelligent_agent()
```

### Batch Processing

```python
from agentds import BenchmarkClient

def process_all_domains():
    client = BenchmarkClient()
    client.start_competition()
    
    domains = client.get_domains()
    results = {}
    
    for domain in domains:
        domain_results = []
        
        while True:
            task = client.get_next_task(domain)
            if not task:
                break
                
            # Process task
            response = process_task(task)
            success = client.submit_response(domain, task.task_number, response)
            domain_results.append(success)
            
        results[domain] = domain_results
    
    return results

def process_task(task):
    # Your task processing logic
    return {"result": "processed"}
```

## Error Handling

```python
from agentds import BenchmarkClient
from agentds.exceptions import AuthenticationError, APIError

try:
    client = BenchmarkClient(api_key="invalid-key", team_name="test")
    client.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/agentds/agentds-bench.git
cd agentds-bench/agentds_pkg
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/agentds/agentds-bench/blob/main/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://agentds.org/docs](https://agentds.org/docs)
- **Issues**: [GitHub Issues](https://github.com/agentds/agentds-bench/issues)
- **Email**: contact@agentds.org

## Changelog

See [CHANGELOG.md](https://github.com/agentds/agentds-bench/blob/main/CHANGELOG.md) for version history. 