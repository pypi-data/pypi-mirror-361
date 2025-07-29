"""
Schema utility functions for capturing dataframe metadata.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def capture_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Capture comprehensive schema information for a dataframe.
    
    Args:
        df: Pandas DataFrame to analyze.
        
    Returns:
        Dictionary containing schema information.
    """
    if df.empty:
        return {
            'columns': [],
            'dtypes': {},
            'null_counts': {},
            'unique_counts': {},
            'memory_usage': {},
            'shape': (0, 0)
        }
    
    schema = {
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'null_counts': df.isnull().sum().to_dict(),
        'unique_counts': df.nunique().to_dict(),
        'memory_usage': df.memory_usage(deep=True).to_dict(),
        'shape': df.shape
    }
    
    # Add basic statistics for numerical columns
    numerical_stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        try:
            numerical_stats[col] = {
                'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                'std': float(df[col].std()) if not df[col].isnull().all() else None,
                'min': float(df[col].min()) if not df[col].isnull().all() else None,
                'max': float(df[col].max()) if not df[col].isnull().all() else None,
                'median': float(df[col].median()) if not df[col].isnull().all() else None,
                'q25': float(df[col].quantile(0.25)) if not df[col].isnull().all() else None,
                'q75': float(df[col].quantile(0.75)) if not df[col].isnull().all() else None,
            }
        except Exception:
            numerical_stats[col] = {}
    
    schema['numerical_stats'] = numerical_stats
    
    # Add basic statistics for categorical columns
    categorical_stats = {}
    for col in df.select_dtypes(include=['object', 'category']).columns:
        try:
            value_counts = df[col].value_counts()
            categorical_stats[col] = {
                'top_values': value_counts.head(10).to_dict(),
                'n_categories': len(value_counts),
                'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            }
        except Exception:
            categorical_stats[col] = {}
    
    schema['categorical_stats'] = categorical_stats
    
    return schema


def detect_schema_drift(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect schema drift between two dataframes.
    
    Args:
        schema1: Schema of the first dataframe.
        schema2: Schema of the second dataframe.
        
    Returns:
        Dictionary containing drift information.
    """
    drift_info = {
        'column_additions': [],
        'column_removals': [],
        'dtype_changes': {},
        'null_count_changes': {},
        'shape_changes': {}
    }
    
    # Check for column additions/removals
    cols1 = set(schema1.get('columns', []))
    cols2 = set(schema2.get('columns', []))
    
    drift_info['column_additions'] = list(cols2 - cols1)
    drift_info['column_removals'] = list(cols1 - cols2)
    
    # Check for dtype changes
    dtypes1 = schema1.get('dtypes', {})
    dtypes2 = schema2.get('dtypes', {})
    
    common_cols = cols1 & cols2
    for col in common_cols:
        if col in dtypes1 and col in dtypes2 and dtypes1[col] != dtypes2[col]:
            drift_info['dtype_changes'][col] = {
                'from': dtypes1[col],
                'to': dtypes2[col]
            }
    
    # Check for null count changes
    null_counts1 = schema1.get('null_counts', {})
    null_counts2 = schema2.get('null_counts', {})
    
    for col in common_cols:
        if col in null_counts1 and col in null_counts2:
            change = null_counts2[col] - null_counts1[col]
            if change != 0:
                drift_info['null_count_changes'][col] = {
                    'change': change,
                    'from': null_counts1[col],
                    'to': null_counts2[col]
                }
    
    # Check for shape changes
    shape1 = schema1.get('shape', (0, 0))
    shape2 = schema2.get('shape', (0, 0))
    
    if shape1 != shape2:
        drift_info['shape_changes'] = {
            'from': shape1,
            'to': shape2,
            'row_change': shape2[0] - shape1[0],
            'column_change': shape2[1] - shape1[1]
        }
    
    return drift_info


def get_schema_summary(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of schema information.
    
    Args:
        schema: Schema dictionary.
        
    Returns:
        Summary dictionary.
    """
    if not schema:
        return {}
    
    return {
        'total_columns': len(schema.get('columns', [])),
        'total_rows': schema.get('shape', (0, 0))[0],
        'null_columns': sum(1 for count in schema.get('null_counts', {}).values() if count > 0),
        'numerical_columns': len(schema.get('numerical_stats', {})),
        'categorical_columns': len(schema.get('categorical_stats', {})),
        'total_memory': sum(schema.get('memory_usage', {}).values()),
        'columns_with_high_cardinality': sum(
            1 for count in schema.get('unique_counts', {}).values() 
            if count > 100
        )
    } 