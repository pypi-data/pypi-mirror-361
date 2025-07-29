"""
Tests for the AuraTrace tracing engine.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from auratrace.core.tracer import Tracer, OperationMetadata, DataframeMetadata


class TestTracer:
    """Test cases for the Tracer class."""
    
    def test_tracer_initialization(self):
        """Test tracer initialization."""
        tracer = Tracer()
        assert tracer.session_id is not None
        assert not tracer.is_active
        assert len(tracer.operations) == 0
        assert len(tracer.dataframes) == 0
    
    def test_start_stop_session(self):
        """Test session start and stop."""
        tracer = Tracer()
        
        # Start session
        tracer.start_session()
        assert tracer.is_active
        assert len(tracer.operations) == 0
        
        # Stop session
        tracer.stop_session()
        assert not tracer.is_active
    
    def test_trace_session_context_manager(self):
        """Test trace session context manager."""
        tracer = Tracer()
        
        with tracer.trace_session():
            assert tracer.is_active
        
        assert not tracer.is_active
    
    def test_capture_dataframe_metadata(self):
        """Test dataframe metadata capture."""
        tracer = Tracer()
        df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
        
        df_id = tracer._capture_dataframe_metadata(df)
        
        assert df_id in tracer.dataframes
        metadata = tracer.dataframes[df_id]
        assert metadata.row_count == 3
        assert metadata.column_count == 2
        assert metadata.memory_usage > 0
    
    def test_wrap_method(self):
        """Test method wrapping functionality."""
        tracer = Tracer()
        tracer.is_active = True
        
        # Create a mock method
        original_method = MagicMock(return_value=pd.DataFrame({'A': [1, 2]}))
        wrapped_method = tracer._wrap_method(original_method, 'test_operation')
        
        # Call the wrapped method
        result = wrapped_method(pd.DataFrame({'B': [1, 2, 3]}))
        
        # Check that the original method was called
        original_method.assert_called_once()
        
        # Check that operation was recorded
        assert len(tracer.operations) == 1
        op = tracer.operations[0]
        assert op.operation_name == 'test_operation'
        assert op.execution_time > 0
    
    def test_patch_unpatch_pandas(self):
        """Test pandas method patching and unpatching."""
        tracer = Tracer()
        tracer.is_active = True
        
        # Store original methods
        original_merge = pd.DataFrame.merge
        original_concat = pd.concat
        
        # Patch pandas
        tracer.patch_pandas()
        
        # Check that methods are wrapped
        assert pd.DataFrame.merge != original_merge
        assert pd.concat != original_concat
        
        # Unpatch pandas
        tracer.unpatch_pandas()
        
        # Check that methods are restored
        assert pd.DataFrame.merge == original_merge
        assert pd.concat == original_concat
    
    def test_get_session_summary_empty(self):
        """Test session summary for empty session."""
        tracer = Tracer()
        summary = tracer.get_session_summary()
        assert summary == {}
    
    def test_get_session_summary_with_operations(self):
        """Test session summary with operations."""
        tracer = Tracer()
        tracer.is_active = True
        
        # Add some mock operations
        op1 = OperationMetadata(
            operation_id="op1",
            operation_name="merge",
            input_ids=["df1"],
            output_ids=["df2"],
            parameters={},
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            timestamp=1234567890.0
        )
        
        op2 = OperationMetadata(
            operation_id="op2",
            operation_name="groupby",
            input_ids=["df2"],
            output_ids=["df3"],
            parameters={},
            execution_time=2.0,
            memory_before=1500,
            memory_after=2000,
            memory_delta=500,
            timestamp=1234567891.0
        )
        
        tracer.operations = [op1, op2]
        
        summary = tracer.get_session_summary()
        
        assert summary['total_operations'] == 2
        assert summary['total_execution_time'] == 3.5
        assert summary['total_memory_delta'] == 1000
        assert summary['operation_counts']['merge'] == 1
        assert summary['operation_counts']['groupby'] == 1


class TestOperationMetadata:
    """Test cases for OperationMetadata."""
    
    def test_operation_metadata_creation(self):
        """Test OperationMetadata creation."""
        op = OperationMetadata(
            operation_id="test_op",
            operation_name="test",
            input_ids=["input1"],
            output_ids=["output1"],
            parameters={"param": "value"},
            execution_time=1.0,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            timestamp=1234567890.0
        )
        
        assert op.operation_id == "test_op"
        assert op.operation_name == "test"
        assert op.execution_time == 1.0
        assert op.memory_delta == 500


class TestDataframeMetadata:
    """Test cases for DataframeMetadata."""
    
    def test_dataframe_metadata_creation(self):
        """Test DataframeMetadata creation."""
        df_meta = DataframeMetadata(
            dataframe_id="test_df",
            dataframe_hash="hash123",
            schema={"columns": ["A", "B"]},
            row_count=100,
            column_count=2,
            memory_usage=1024,
            timestamp=1234567890.0
        )
        
        assert df_meta.dataframe_id == "test_df"
        assert df_meta.row_count == 100
        assert df_meta.column_count == 2
        assert df_meta.memory_usage == 1024


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': [1.1, 2.2, 3.3, 4.4, 5.5]
    })


@pytest.fixture
def tracer_with_data(tracer, sample_dataframe):
    """Create a tracer with sample data."""
    tracer.is_active = True
    df_id = tracer._capture_dataframe_metadata(sample_dataframe)
    return tracer, df_id


@pytest.fixture
def tracer():
    """Create a fresh tracer instance."""
    return Tracer()


class TestTracerIntegration:
    """Integration tests for the tracer."""
    
    def test_trace_pandas_operations(self, tracer):
        """Test tracing actual pandas operations."""
        with tracer.trace_session():
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            df_filtered = df[df['A'] > 1]
            df_grouped = df_filtered.groupby('B').sum()
        
        summary = tracer.get_session_summary()
        assert summary['total_operations'] > 0
        assert summary['dataframe_count'] > 0
    
    def test_memory_tracking(self, tracer):
        """Test memory usage tracking."""
        with tracer.trace_session():
            # Create a large dataframe
            df = pd.DataFrame(np.random.randn(1000, 100))
            # Perform some operations
            df_filtered = df.dropna()
            df_grouped = df_filtered.groupby(df_filtered.columns[0]).mean()
        
        summary = tracer.get_session_summary()
        assert summary['total_memory_delta'] != 0
    
    def test_operation_parameters_capture(self, tracer):
        """Test that operation parameters are captured."""
        with tracer.trace_session():
            df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
            # Perform operations with parameters
            df_dropped = df.dropna(how='any')
            df_sorted = df_dropped.sort_values('A', ascending=False)
        
        # Check that operations have parameters
        for op in tracer.operations:
            assert 'parameters' in op.__dict__
            assert isinstance(op.parameters, dict) 