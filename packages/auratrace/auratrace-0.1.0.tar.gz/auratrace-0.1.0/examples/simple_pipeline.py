#!/usr/bin/env python3
"""
Simple data pipeline example for AuraTrace demonstration.
"""

import pandas as pd
import numpy as np
from auratrace import Tracer

def main():
    """Run a simple data pipeline with AuraTrace tracing."""
    
    # Create sample data
    print("Creating sample data...")
    data = {
        'user_id': range(1, 1001),
        'name': [f'User_{i}' for i in range(1, 1001)],
        'age': np.random.randint(18, 80, 1000),
        'email': [f'user{i}@example.com' for i in range(1, 1001)],
        'score': np.random.normal(75, 15, 1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000)
    }
    
    df = pd.DataFrame(data)
    print(f"Initial data shape: {df.shape}")
    
    # Data cleaning
    print("\nCleaning data...")
    df_clean = df.dropna()
    print(f"After dropna: {df_clean.shape}")
    
    # Filter data
    print("\nFiltering data...")
    df_filtered = df_clean[df_clean['age'] >= 21]
    print(f"After age filter: {df_filtered.shape}")
    
    # Group by and aggregate
    print("\nAggregating data...")
    df_agg = df_filtered.groupby('category').agg({
        'age': ['mean', 'std'],
        'score': ['mean', 'count']
    }).round(2)
    print(f"Aggregation result shape: {df_agg.shape}")
    
    # Sort data
    print("\nSorting data...")
    df_sorted = df_filtered.sort_values('score', ascending=False)
    print(f"Sorted data shape: {df_sorted.shape}")
    
    # Create summary statistics
    print("\nCreating summary...")
    summary = df_sorted.describe()
    print(f"Summary shape: {summary.shape}")
    
    print("\nPipeline completed successfully!")
    return df_sorted

if __name__ == "__main__":
    # Run with AuraTrace tracing
    with Tracer().trace_session():
        result = main()
        print(f"\nFinal result shape: {result.shape}") 