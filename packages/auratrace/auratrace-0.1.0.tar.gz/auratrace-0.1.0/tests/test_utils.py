"""
Tests for the AuraTrace utility modules.
"""

import pytest
import pandas as pd
import numpy as np
import psutil
import os
import json
import yaml
from unittest.mock import Mock, patch
from datetime import datetime

from auratrace.utils.memory import get_memory_usage, get_memory_percentage, get_system_memory_info
from auratrace.utils.schema import capture_schema, detect_schema_drift, get_schema_summary
from auratrace.utils.formatting import format_bytes, format_time, format_percentage, format_number, format_duration, truncate_string, format_list


class TestMemoryUtils:
    """Test cases for memory utility functions."""
    
    def test_get_memory_usage(self):
        """Test getting memory usage."""
        memory_usage = get_memory_usage()
        
        assert isinstance(memory_usage, int)
        assert memory_usage > 0
    
    def test_get_memory_percentage(self):
        """Test getting memory percentage."""
        memory_percent = get_memory_percentage()
        
        assert isinstance(memory_percent, float)
        assert 0 <= memory_percent <= 100
    
    def test_get_system_memory_info(self):
        """Test getting system memory information."""
        memory_info = get_system_memory_info()
        
        assert isinstance(memory_info, dict)
        assert 'total' in memory_info
        assert 'available' in memory_info
        assert 'used' in memory_info
        assert 'free' in memory_info
        assert 'percent' in memory_info
        assert memory_info['total'] > 0


class TestSchemaUtils:
    """Test cases for schema utility functions."""
    
    def test_capture_schema_basic(self):
        """Test basic schema capture."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c'],
            'C': [1.5, 2.5, 3.5]
        })
        
        schema = capture_schema(df)
        
        assert 'shape' in schema
        assert 'columns' in schema
        assert 'dtypes' in schema
        assert schema['shape'] == (3, 3)
        assert len(schema['columns']) == 3
        assert len(schema['dtypes']) == 3
    
    def test_capture_schema_empty_dataframe(self):
        """Test schema capture for empty dataframe."""
        df = pd.DataFrame()
        
        schema = capture_schema(df)
        
        assert schema['shape'] == (0, 0)
        assert len(schema['columns']) == 0
        assert len(schema['dtypes']) == 0
    
    def test_capture_schema_with_nulls(self):
        """Test schema capture with null values."""
        df = pd.DataFrame({
            'A': [1, None, 3],
            'B': ['a', 'b', None],
            'C': [1.5, 2.5, 3.5]
        })
        
        schema = capture_schema(df)
        
        assert 'null_counts' in schema
        assert schema['null_counts']['A'] == 1
        assert schema['null_counts']['B'] == 1
        assert schema['null_counts']['C'] == 0
    
    def test_capture_schema_with_numerical_stats(self):
        """Test schema capture with numerical statistics."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        schema = capture_schema(df)
        
        assert 'numerical_stats' in schema
        assert 'A' in schema['numerical_stats']
        assert 'B' in schema['numerical_stats']
        assert 'mean' in schema['numerical_stats']['A']
        assert 'std' in schema['numerical_stats']['A']
    
    def test_detect_schema_drift(self):
        """Test schema drift detection."""
        df1 = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        df2 = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': ['a', 'b', 'c', 'd'],
            'C': [1.1, 2.2, 3.3, 4.4]
        })
        
        schema1 = capture_schema(df1)
        schema2 = capture_schema(df2)
        
        drift = detect_schema_drift(schema1, schema2)
        
        assert 'column_additions' in drift
        assert 'column_removals' in drift
        assert 'C' in drift['column_additions']
        assert len(drift['column_removals']) == 0
    
    def test_get_schema_summary(self):
        """Test schema summary generation."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c'],
            'C': [1.1, 2.2, 3.3]
        })
        
        schema = capture_schema(df)
        summary = get_schema_summary(schema)
        
        assert 'total_columns' in summary
        assert 'total_rows' in summary
        assert summary['total_columns'] == 3
        assert summary['total_rows'] == 3


class TestFormattingUtils:
    """Test cases for formatting utility functions."""
    
    def test_format_bytes_basic(self):
        """Test basic byte formatting."""
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(0) == "0 B"
    
    def test_format_time_basic(self):
        """Test basic time formatting."""
        assert "ms" in format_time(0.5)
        assert "s" in format_time(30)
        assert "m" in format_time(90)
        assert "h" in format_time(3600)
    
    def test_format_percentage_basic(self):
        """Test percentage formatting."""
        assert format_percentage(50, 100) == "50.0%"
        assert format_percentage(0, 100) == "0.0%"
        assert format_percentage(100, 100) == "100.0%"
    
    def test_format_number_basic(self):
        """Test number formatting."""
        assert format_number(500) == "500"
        assert "K" in format_number(1500)
        assert "M" in format_number(1500000)
        assert "B" in format_number(1500000000)
    
    def test_format_duration(self):
        """Test duration formatting."""
        duration = format_duration(1000, 1030)
        assert "s" in duration
    
    def test_truncate_string(self):
        """Test string truncation."""
        long_string = "This is a very long string that should be truncated"
        truncated = truncate_string(long_string, 20)
        assert len(truncated) <= 20
        assert "..." in truncated
    
    def test_format_list(self):
        """Test list formatting."""
        short_list = [1, 2, 3]
        assert format_list(short_list) == "[1, 2, 3]"
        
        long_list = list(range(10))
        formatted = format_list(long_list, 3)
        assert "..." in formatted
        assert "more" in formatted


class TestIntegrationUtils:
    """Integration tests for utility functions."""
    
    def test_memory_and_formatting_integration(self):
        """Test integration between memory and formatting functions."""
        memory_usage = get_memory_usage()
        formatted_memory = format_bytes(memory_usage)
        
        assert isinstance(formatted_memory, str)
        assert len(formatted_memory) > 0
    
    def test_schema_and_formatting_integration(self):
        """Test integration between schema and formatting functions."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        
        schema = capture_schema(df)
        summary = get_schema_summary(schema)
        
        # Format the summary values
        total_memory = format_bytes(summary.get('total_memory', 0))
        assert isinstance(total_memory, str)
    
    def test_comprehensive_workflow(self):
        """Test a comprehensive workflow using multiple utilities."""
        # Create test data
        df = pd.DataFrame({
            'id': range(100),
            'value': np.random.randn(100),
            'category': ['A', 'B', 'C'] * 33 + ['A']
        })
        
        # Capture schema
        schema = capture_schema(df)
        
        # Get memory info
        memory_info = get_system_memory_info()
        
        # Format results
        memory_usage = format_bytes(memory_info['used'])
        total_memory = format_bytes(memory_info['total'])
        
        # Verify all functions work together
        assert isinstance(schema, dict)
        assert isinstance(memory_usage, str)
        assert isinstance(total_memory, str)
        assert schema['shape'] == (100, 3) 