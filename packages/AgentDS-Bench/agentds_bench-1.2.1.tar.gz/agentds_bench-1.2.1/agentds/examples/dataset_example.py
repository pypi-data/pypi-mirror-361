"""
Dataset loading example for AgentDS Python client.

This example demonstrates how to:
- Load datasets directly from the platform
- Explore dataset information
- Work with pandas DataFrames
- Implement basic data analysis
"""

import pandas as pd
from typing import Tuple

from agentds import BenchmarkClient
from agentds.exceptions import DatasetError, AuthenticationError


def analyze_dataset(train_df: pd.DataFrame, test_df: pd.DataFrame, sample_df: pd.DataFrame) -> dict:
    """
    Perform basic analysis on the loaded dataset.
    
    Args:
        train_df: Training data
        test_df: Test data  
        sample_df: Sample submission data
        
    Returns:
        Dictionary containing analysis results
    """
    analysis = {
        "train_shape": train_df.shape,
        "test_shape": test_df.shape,
        "sample_shape": sample_df.shape,
        "train_columns": list(train_df.columns),
        "test_columns": list(test_df.columns),
        "sample_columns": list(sample_df.columns),
        "train_dtypes": train_df.dtypes.to_dict(),
        "missing_values": train_df.isnull().sum().to_dict(),
    }
    
    # Basic statistics for numeric columns
    numeric_cols = train_df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        analysis["numeric_stats"] = train_df[numeric_cols].describe().to_dict()
    
    return analysis


def demonstrate_dataset_loading():
    """Demonstrate dataset loading capabilities."""
    try:
        # Initialize client
        client = BenchmarkClient()
        
        # Get available domains
        domains = client.get_domains()
        print(f"Available domains: {domains}")
        
        for domain in domains[:2]:  # Process first 2 domains for demonstration
            print(f"\n{'='*50}")
            print(f"Processing domain: {domain}")
            print(f"{'='*50}")
            
            try:
                # Method 1: Get dataset info without loading full data
                print("\n1. Getting dataset information...")
                info = client.get_dataset_info(domain)
                print(f"Dataset info for {domain}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                
                # Method 2: Load full dataset
                print("\n2. Loading full dataset...")
                train_df, test_df, sample_df = client.load_dataset(domain)
                
                print(f"Loaded dataset for '{domain}':")
                print(f"  Train: {train_df.shape[0]:,} rows × {train_df.shape[1]} columns")
                print(f"  Test: {test_df.shape[0]:,} rows × {test_df.shape[1]} columns")
                print(f"  Sample: {sample_df.shape[0]:,} rows × {sample_df.shape[1]} columns")
                
                # Method 3: Analyze the data
                print("\n3. Analyzing dataset...")
                analysis = analyze_dataset(train_df, test_df, sample_df)
                
                print(f"Training data columns: {analysis['train_columns']}")
                print(f"Data types: {list(analysis['train_dtypes'].keys())}")
                
                if analysis.get('missing_values'):
                    missing_cols = [col for col, count in analysis['missing_values'].items() if count > 0]
                    if missing_cols:
                        print(f"Columns with missing values: {missing_cols}")
                    else:
                        print("No missing values found")
                
                # Display first few rows
                print("\n4. Sample data:")
                print(train_df.head())
                
            except DatasetError as e:
                print(f"Dataset error for {domain}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error for {domain}: {e}")
                continue
                
    except AuthenticationError as e:
        print(f"Authentication error: {e}")
        print("Please ensure you have valid credentials set")
    except Exception as e:
        print(f"Unexpected error: {e}")


def demonstrate_task_dataset_loading():
    """Demonstrate loading datasets through tasks."""
    try:
        client = BenchmarkClient()
        client.start_competition()
        
        domains = client.get_domains()
        
        if domains:
            domain = domains[0]
            task = client.get_next_task(domain)
            
            if task:
                print(f"\nLoading dataset for task #{task.task_number} in {task.domain}")
                
                # Load dataset through task (convenience method)
                train_df, test_df, sample_df = task.load_dataset()
                
                print(f"Dataset loaded via task:")
                print(f"  Train: {train_df.shape}")
                print(f"  Test: {test_df.shape}")
                print(f"  Sample: {sample_df.shape}")
                
            else:
                print(f"No tasks available for domain {domain}")
        else:
            print("No domains available")
            
    except Exception as e:
        print(f"Error in task dataset loading: {e}")


def main():
    """Main demonstration function."""
    print("AgentDS Dataset Loading Examples")
    print("=" * 40)
    
    print("\nDemonstrating direct dataset loading...")
    demonstrate_dataset_loading()
    
    print("\n" + "="*60)
    print("\nDemonstrating task-based dataset loading...")
    demonstrate_task_dataset_loading()


if __name__ == "__main__":
    main() 