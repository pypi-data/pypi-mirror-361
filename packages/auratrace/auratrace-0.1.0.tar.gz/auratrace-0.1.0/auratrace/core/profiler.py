"""
Data profiling engine for capturing detailed statistics about dataframes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re

from ..utils.schema import capture_schema


@dataclass
class ColumnProfile:
    """Profile information for a single column."""
    
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    memory_usage: int
    
    # Numerical statistics
    mean: Optional[float] = None
    std: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    median: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    
    # Categorical statistics
    top_values: Optional[Dict[str, int]] = None
    most_frequent: Optional[str] = None
    most_frequent_count: Optional[int] = None
    
    # String statistics
    avg_length: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    # PII detection
    pii_score: float = 0.0
    pii_type: Optional[str] = None


@dataclass
class DataframeProfile:
    """Complete profile of a dataframe."""
    
    shape: Tuple[int, int]
    total_memory: int
    columns: List[ColumnProfile]
    schema_summary: Dict[str, Any]
    profiling_time: float
    
    @property
    def row_count(self) -> int:
        return self.shape[0]
    
    @property
    def column_count(self) -> int:
        return self.shape[1]
    
    @property
    def null_columns(self) -> List[ColumnProfile]:
        return [col for col in self.columns if col.null_count > 0]
    
    @property
    def numerical_columns(self) -> List[ColumnProfile]:
        return [col for col in self.columns if col.mean is not None]
    
    @property
    def categorical_columns(self) -> List[ColumnProfile]:
        return [col for col in self.columns if col.top_values is not None]
    
    @property
    def high_cardinality_columns(self) -> List[ColumnProfile]:
        return [col for col in self.columns if col.unique_percentage > 0.5]


class DataProfiler:
    """
    Data profiling engine for capturing detailed statistics.
    
    This class provides comprehensive profiling capabilities including
    statistical analysis, PII detection, and data quality metrics.
    """
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'date': r'\b\d{4}-\d{2}-\d{2}\b',
        }
    
    def profile_dataframe(self, df: pd.DataFrame) -> DataframeProfile:
        """
        Create a comprehensive profile of a dataframe.
        
        Args:
            df: Pandas DataFrame to profile.
            
        Returns:
            DataframeProfile object with detailed statistics.
        """
        import time
        start_time = time.time()
        
        columns = []
        for col in df.columns:
            column_profile = self._profile_column(df, col)
            columns.append(column_profile)
        
        profiling_time = time.time() - start_time
        
        return DataframeProfile(
            shape=df.shape,
            total_memory=df.memory_usage(deep=True).sum(),
            columns=columns,
            schema_summary=capture_schema(df),
            profiling_time=profiling_time
        )
    
    def _profile_column(self, df: pd.DataFrame, column: str) -> ColumnProfile:
        """
        Profile a single column.
        
        Args:
            df: DataFrame containing the column.
            column: Name of the column to profile.
            
        Returns:
            ColumnProfile object with detailed statistics.
        """
        series = df[column]
        dtype = str(series.dtype)
        null_count = series.isnull().sum()
        null_percentage = (null_count / len(series)) * 100 if len(series) > 0 else 0
        unique_count = series.nunique()
        unique_percentage = (unique_count / len(series)) * 100 if len(series) > 0 else 0
        memory_usage = series.memory_usage(deep=True)
        
        profile = ColumnProfile(
            name=column,
            dtype=dtype,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            memory_usage=memory_usage
        )
        
        # Add numerical statistics
        if np.issubdtype(series.dtype, np.number):
            self._add_numerical_stats(profile, series)
        
        # Add categorical statistics
        if series.dtype == 'object' or series.dtype.name == 'category':
            self._add_categorical_stats(profile, series)
            self._add_string_stats(profile, series)
        
        # Add PII detection
        self._detect_pii(profile, series)
        
        return profile
    
    def _add_numerical_stats(self, profile: ColumnProfile, series: pd.Series) -> None:
        """Add numerical statistics to a column profile."""
        try:
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                profile.mean = float(non_null_series.mean())
                profile.std = float(non_null_series.std())
                profile.min_value = float(non_null_series.min())
                profile.max_value = float(non_null_series.max())
                profile.median = float(non_null_series.median())
                profile.q25 = float(non_null_series.quantile(0.25))
                profile.q75 = float(non_null_series.quantile(0.75))
        except Exception:
            pass
    
    def _add_categorical_stats(self, profile: ColumnProfile, series: pd.Series) -> None:
        """Add categorical statistics to a column profile."""
        try:
            value_counts = series.value_counts()
            if len(value_counts) > 0:
                profile.top_values = value_counts.head(10).to_dict()
                profile.most_frequent = str(value_counts.index[0])
                profile.most_frequent_count = int(value_counts.iloc[0])
        except Exception:
            pass
    
    def _add_string_stats(self, profile: ColumnProfile, series: pd.Series) -> None:
        """Add string statistics to a column profile."""
        try:
            # Convert to string and get length statistics
            string_series = series.astype(str)
            lengths = string_series.str.len()
            
            profile.avg_length = float(lengths.mean())
            profile.min_length = int(lengths.min())
            profile.max_length = int(lengths.max())
        except Exception:
            pass
    
    def _detect_pii(self, profile: ColumnProfile, series: pd.Series) -> None:
        """Detect potential PII in a column."""
        try:
            # Sample the data for PII detection
            sample_size = min(1000, len(series))
            sample = series.dropna().sample(n=sample_size, random_state=42)
            
            pii_scores = {}
            for pii_type, pattern in self.pii_patterns.items():
                matches = sample.astype(str).str.match(pattern, na=False)
                match_rate = matches.sum() / len(sample) if len(sample) > 0 else 0
                pii_scores[pii_type] = match_rate
            
            # Find the highest scoring PII type
            if pii_scores:
                best_type = max(pii_scores.items(), key=lambda x: x[1])
                profile.pii_type = best_type[0] if best_type[1] > 0.1 else None
                profile.pii_score = best_type[1]
        except Exception:
            pass
    
    def detect_anomalies(self, profile: DataframeProfile) -> Dict[str, Any]:
        """
        Detect potential data quality anomalies.
        
        Args:
            profile: DataframeProfile to analyze.
            
        Returns:
            Dictionary containing detected anomalies.
        """
        anomalies = {
            'high_null_columns': [],
            'low_cardinality_columns': [],
            'high_cardinality_columns': [],
            'potential_pii_columns': [],
            'memory_intensive_columns': [],
            'outliers': []
        }
        
        for col in profile.columns:
            # High null percentage
            if col.null_percentage > 50:
                anomalies['high_null_columns'].append({
                    'column': col.name,
                    'null_percentage': col.null_percentage
                })
            
            # Low cardinality
            if col.unique_percentage < 1.0 and col.unique_count > 1:
                anomalies['low_cardinality_columns'].append({
                    'column': col.name,
                    'unique_percentage': col.unique_percentage
                })
            
            # High cardinality
            if col.unique_percentage > 0.9:
                anomalies['high_cardinality_columns'].append({
                    'column': col.name,
                    'unique_percentage': col.unique_percentage
                })
            
            # Potential PII
            if col.pii_score > 0.3:
                anomalies['potential_pii_columns'].append({
                    'column': col.name,
                    'pii_type': col.pii_type,
                    'pii_score': col.pii_score
                })
            
            # Memory intensive
            if col.memory_usage > profile.total_memory * 0.1:
                anomalies['memory_intensive_columns'].append({
                    'column': col.name,
                    'memory_usage': col.memory_usage
                })
        
        return anomalies
    
    def generate_summary_report(self, profile: DataframeProfile) -> Dict[str, Any]:
        """
        Generate a summary report of the dataframe profile.
        
        Args:
            profile: DataframeProfile to summarize.
            
        Returns:
            Dictionary containing summary information.
        """
        return {
            'shape': profile.shape,
            'total_memory': profile.total_memory,
            'total_columns': profile.column_count,
            'total_rows': profile.row_count,
            'null_columns_count': len(profile.null_columns),
            'numerical_columns': len(profile.numerical_columns),
            'categorical_columns': len(profile.categorical_columns),
            'high_cardinality_columns_count': len(profile.high_cardinality_columns),
            'profiling_time': profile.profiling_time,
            'anomalies': self.detect_anomalies(profile)
        } 