"""
Tests for the AuraTrace data profiler.
"""

import pytest
import pandas as pd
import numpy as np
from auratrace.core.profiler import DataProfiler, ColumnProfile, DataframeProfile


class TestDataProfiler:
    """Test cases for the DataProfiler class."""
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        profiler = DataProfiler()
        assert len(profiler.pii_patterns) > 0
        assert 'email' in profiler.pii_patterns
        assert 'phone' in profiler.pii_patterns
    
    def test_profile_dataframe_basic(self):
        """Test basic dataframe profiling."""
        profiler = DataProfiler()
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        profile = profiler.profile_dataframe(df)
        
        assert isinstance(profile, DataframeProfile)
        assert profile.shape == (5, 3)
        assert profile.column_count == 3
        assert profile.row_count == 5
        assert len(profile.columns) == 3
        assert profile.total_memory > 0
        assert profile.profiling_time >= 0
    
    def test_profile_dataframe_empty(self):
        """Test profiling empty dataframe."""
        profiler = DataProfiler()
        df = pd.DataFrame()
        
        profile = profiler.profile_dataframe(df)
        
        assert profile.shape == (0, 0)
        assert profile.column_count == 0
        assert profile.row_count == 0
        assert len(profile.columns) == 0
    
    def test_profile_column_numerical(self):
        """Test profiling numerical column."""
        profiler = DataProfiler()
        df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        
        column_profile = profiler._profile_column(df, 'A')
        
        assert column_profile.name == 'A'
        assert column_profile.dtype == 'int64'
        assert column_profile.null_count == 0
        assert column_profile.null_percentage == 0.0
        assert column_profile.unique_count == 5
        assert column_profile.unique_percentage == 100.0
        assert column_profile.mean == 3.0
        assert column_profile.std == 1.5811388300841898
        assert column_profile.min_value == 1
        assert column_profile.max_value == 5
    
    def test_profile_column_categorical(self):
        """Test profiling categorical column."""
        profiler = DataProfiler()
        df = pd.DataFrame({'A': ['a', 'b', 'a', 'c', 'b']})
        
        column_profile = profiler._profile_column(df, 'A')
        
        assert column_profile.name == 'A'
        assert column_profile.dtype == 'object'
        assert column_profile.null_count == 0
        assert column_profile.unique_count == 3
        assert column_profile.top_values is not None
        assert 'a' in column_profile.top_values
        assert 'b' in column_profile.top_values
    
    def test_profile_column_with_nulls(self):
        """Test profiling column with null values."""
        profiler = DataProfiler()
        df = pd.DataFrame({'A': [1, 2, None, 4, 5]})
        
        column_profile = profiler._profile_column(df, 'A')
        
        assert column_profile.null_count == 1
        assert column_profile.null_percentage == 20.0
        assert column_profile.unique_count == 4  # excluding None
    
    def test_detect_pii_email(self):
        """Test PII detection for email addresses."""
        profiler = DataProfiler()
        df = pd.DataFrame({
            'email': ['test@example.com', 'user@domain.org', 'invalid-email']
        })
        
        column_profile = profiler._profile_column(df, 'email')
        
        assert column_profile.pii_score > 0
        assert column_profile.pii_type == 'email'
    
    def test_detect_pii_phone(self):
        """Test PII detection for phone numbers."""
        profiler = DataProfiler()
        df = pd.DataFrame({
            'phone': ['123-456-7890', '987.654.3210', '555-1234']
        })
        
        column_profile = profiler._profile_column(df, 'phone')
        
        assert column_profile.pii_score > 0
        assert column_profile.pii_type == 'phone'
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        profiler = DataProfiler()
        
        # Create dataframe with potential anomalies
        n = 1000
        df = pd.DataFrame({
            'A': list(range(1, n+1)),
            'B': [None] * n,  # High null percentage
            'C': ['a'] * (n-5) + ['b'] * 5,  # Low cardinality (2 unique values, <0.01%)
            'D': list(range(n)),  # High cardinality
            'E': ['test@example.com'] * n  # Potential PII
        })
        
        profile = profiler.profile_dataframe(df)
        anomalies = profiler.detect_anomalies(profile)
        
        # Should detect high null percentage
        assert len(anomalies['high_null_columns']) > 0
        
        # Should detect low cardinality
        assert len(anomalies['low_cardinality_columns']) > 0
        
        # Should detect high cardinality
        assert len(anomalies['high_cardinality_columns']) > 0
        
        # Should detect potential PII
        assert len(anomalies['potential_pii_columns']) > 0
    
    def test_generate_summary_report(self):
        """Test summary report generation."""
        profiler = DataProfiler()
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        profile = profiler.profile_dataframe(df)
        summary = profiler.generate_summary_report(profile)
        
        assert summary['total_columns'] == 3
        assert summary['total_rows'] == 5
        assert summary['numerical_columns'] == 2
        assert summary['categorical_columns'] == 1
        assert 'anomalies' in summary


class TestColumnProfile:
    """Test cases for ColumnProfile."""
    
    def test_column_profile_creation(self):
        """Test ColumnProfile creation."""
        profile = ColumnProfile(
            name='test_column',
            dtype='int64',
            null_count=0,
            null_percentage=0.0,
            unique_count=5,
            unique_percentage=100.0,
            memory_usage=1024,
            mean=3.0,
            std=1.5,
            min_value=1,
            max_value=5
        )
        
        assert profile.name == 'test_column'
        assert profile.dtype == 'int64'
        assert profile.null_count == 0
        assert profile.mean == 3.0
        assert profile.min_value == 1
        assert profile.max_value == 5
    
    def test_column_profile_with_pii(self):
        """Test ColumnProfile with PII detection."""
        profile = ColumnProfile(
            name='email',
            dtype='object',
            null_count=0,
            null_percentage=0.0,
            unique_count=10,
            unique_percentage=50.0,
            memory_usage=1024,
            pii_score=0.8,
            pii_type='email'
        )
        
        assert profile.pii_score == 0.8
        assert profile.pii_type == 'email'


class TestDataframeProfile:
    """Test cases for DataframeProfile."""
    
    def test_dataframe_profile_creation(self):
        """Test DataframeProfile creation."""
        columns = [
            ColumnProfile(
                name='A',
                dtype='int64',
                null_count=0,
                null_percentage=0.0,
                unique_count=5,
                unique_percentage=100.0,
                memory_usage=1024,
                mean=3.0
            ),
            ColumnProfile(
                name='B',
                dtype='object',
                null_count=1,
                null_percentage=20.0,
                unique_count=4,
                unique_percentage=80.0,
                memory_usage=1024,
                top_values={'a': 3, 'b': 1}
            )
        ]
        
        profile = DataframeProfile(
            shape=(5, 2),
            total_memory=2048,
            columns=columns,
            schema_summary={},
            profiling_time=0.1
        )
        
        assert profile.shape == (5, 2)
        assert profile.row_count == 5
        assert profile.column_count == 2
        assert len(profile.null_columns) == 1
        assert len(profile.numerical_columns) == 1
        assert len(profile.categorical_columns) == 1
    
    def test_dataframe_profile_properties(self):
        """Test DataframeProfile properties."""
        columns = [
            ColumnProfile(
                name='A',
                dtype='int64',
                null_count=0,
                null_percentage=0.0,
                unique_count=5,
                unique_percentage=100.0,
                memory_usage=1024,
                mean=3.0
            ),
            ColumnProfile(
                name='B',
                dtype='object',
                null_count=0,
                null_percentage=0.0,
                unique_count=5,
                unique_percentage=100.0,
                memory_usage=1024,
                top_values={'a': 3, 'b': 2}
            )
        ]
        
        profile = DataframeProfile(
            shape=(5, 2),
            total_memory=2048,
            columns=columns,
            schema_summary={},
            profiling_time=0.1
        )
        
        # Test null columns
        assert len(profile.null_columns) == 0
        
        # Test numerical columns
        assert len(profile.numerical_columns) == 1
        
        # Test categorical columns
        assert len(profile.categorical_columns) == 1
        
        # Test high cardinality columns
        assert len(profile.high_cardinality_columns) == 2


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5],
        'D': ['test@example.com', 'user@domain.org', 'admin@company.com', 'support@help.com', 'info@site.com']
    })


@pytest.fixture
def profiler():
    """Create a fresh profiler instance."""
    return DataProfiler()


class TestProfilerIntegration:
    """Integration tests for the profiler."""
    
    def test_profile_complex_dataframe(self, profiler, sample_dataframe):
        """Test profiling a complex dataframe."""
        profile = profiler.profile_dataframe(sample_dataframe)
        
        assert profile.shape == (5, 4)
        assert profile.column_count == 4
        assert profile.row_count == 5
        
        # Check that all columns were profiled
        assert len(profile.columns) == 4
        
        # Check numerical column profiling
        numerical_cols = [col for col in profile.columns if col.mean is not None]
        assert len(numerical_cols) == 2  # A and C columns
        
        # Check categorical column profiling
        categorical_cols = [col for col in profile.columns if col.top_values is not None]
        assert len(categorical_cols) == 2  # B and D columns
        
        # Check PII detection
        pii_cols = [col for col in profile.columns if col.pii_score > 0]
        assert len(pii_cols) > 0  # Should detect email addresses
    
    def test_anomaly_detection_integration(self, profiler):
        """Test anomaly detection with real data."""
        # Create dataframe with various anomalies
        n = 1000
        df = pd.DataFrame({
            'id': range(n),  # High cardinality
            'status': ['active'] * (n-1) + ['inactive'],  # Low cardinality (2 unique values, <0.01%)
            'email': [f'user{i}@example.com' for i in range(n)],  # PII
            'score': np.random.normal(75, 15, n),  # Normal distribution
            'null_col': [None] * n,  # All nulls
            'mixed': [i if i % 2 == 0 else None for i in range(n)]  # Mixed nulls
        })
        
        profile = profiler.profile_dataframe(df)
        anomalies = profiler.detect_anomalies(profile)
        
        # Should detect various types of anomalies
        assert len(anomalies['high_null_columns']) > 0
        assert len(anomalies['low_cardinality_columns']) > 0
        assert len(anomalies['high_cardinality_columns']) > 0
        assert len(anomalies['potential_pii_columns']) > 0
    
    def test_performance_profiling(self, profiler):
        """Test that profiling doesn't take too long."""
        import time
        
        # Create a larger dataframe
        df = pd.DataFrame({
            'A': range(10000),
            'B': [f'value_{i}' for i in range(10000)],
            'C': np.random.normal(0, 1, 10000)
        })
        
        start_time = time.time()
        profile = profiler.profile_dataframe(df)
        end_time = time.time()
        
        # Profiling should complete within reasonable time (e.g., 5 seconds)
        assert end_time - start_time < 5.0
        
        # Should have profiled all columns
        assert len(profile.columns) == 3
        assert profile.shape == (10000, 3) 