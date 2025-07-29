"""
Core tracing engine for intercepting data operations.
"""

import uuid
import time
import functools
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
import pandas as pd
import psutil
import os

from ..utils.memory import get_memory_usage
from ..utils.schema import capture_schema


@dataclass
class OperationMetadata:
    """Metadata for a single data operation."""
    
    operation_id: str
    operation_name: str
    input_ids: List[str]
    output_ids: List[str]
    parameters: Dict[str, Any]
    execution_time: float
    memory_before: int
    memory_after: int
    memory_delta: int
    timestamp: float
    schema_before: Optional[Dict] = None
    schema_after: Optional[Dict] = None
    row_count_before: Optional[int] = None
    row_count_after: Optional[int] = None
    column_count_before: Optional[int] = None
    column_count_after: Optional[int] = None


@dataclass
class DataframeMetadata:
    """Metadata for a dataframe."""
    
    dataframe_id: str
    dataframe_hash: str
    schema: Dict[str, Any]
    row_count: int
    column_count: int
    memory_usage: int
    timestamp: float
    source_operation_id: Optional[str] = None


class Tracer:
    """
    Core tracing engine that intercepts pandas operations.
    
    This class provides the foundation for capturing data lineage by
    wrapping pandas operations and recording metadata about each transformation.
    """
    
    def __init__(self):
        self.operations: List[OperationMetadata] = []
        self.dataframes: Dict[str, DataframeMetadata] = {}
        self.session_id = str(uuid.uuid4())
        self.is_active = False
        self._original_methods = {}
        self._process = psutil.Process(os.getpid())
        
    def start_session(self) -> None:
        """Start a new tracing session."""
        self.is_active = True
        self.operations.clear()
        self.dataframes.clear()
        self.session_id = str(uuid.uuid4())
        
    def stop_session(self) -> None:
        """Stop the current tracing session."""
        self.is_active = False
        
    def _generate_dataframe_id(self, df: pd.DataFrame) -> str:
        """Generate a unique ID for a dataframe."""
        return str(uuid.uuid4())
    
    def _capture_dataframe_metadata(self, df: pd.DataFrame, operation_id: Optional[str] = None) -> str:
        """Capture metadata for a dataframe and return its ID."""
        df_id = self._generate_dataframe_id(df)
        
        metadata = DataframeMetadata(
            dataframe_id=df_id,
            dataframe_hash=str(hash(df.to_string())),
            schema=capture_schema(df),
            row_count=len(df),
            column_count=len(df.columns),
            memory_usage=df.memory_usage(deep=True).sum(),
            timestamp=time.time(),
            source_operation_id=operation_id
        )
        
        self.dataframes[df_id] = metadata
        return df_id
    
    def _wrap_method(self, method: Callable, operation_name: str) -> Callable:
        """Wrap a pandas method to capture metadata."""
        
        @functools.wraps(method)
        def wrapped_method(*args, **kwargs):
            if not self.is_active:
                return method(*args, **kwargs)
            
            # Capture memory before
            memory_before = get_memory_usage(self._process)
            start_time = time.time()
            
            # Capture input metadata
            input_ids = []
            for arg in args:
                if isinstance(arg, pd.DataFrame):
                    input_ids.append(self._capture_dataframe_metadata(arg))
            
            # Execute the original method
            result = method(*args, **kwargs)
            
            # Capture execution time and memory after
            execution_time = time.time() - start_time
            memory_after = get_memory_usage(self._process)
            memory_delta = memory_after - memory_before
            
            # Capture output metadata
            output_ids = []
            if isinstance(result, pd.DataFrame):
                output_ids.append(self._capture_dataframe_metadata(result, str(uuid.uuid4())))
            elif isinstance(result, tuple):
                for item in result:
                    if isinstance(item, pd.DataFrame):
                        output_ids.append(self._capture_dataframe_metadata(item, str(uuid.uuid4())))
            
            # Record operation metadata
            operation_metadata = OperationMetadata(
                operation_id=str(uuid.uuid4()),
                operation_name=operation_name,
                input_ids=input_ids,
                output_ids=output_ids,
                parameters={
                    'args': [str(type(arg)) for arg in args],
                    'kwargs': kwargs
                },
                execution_time=execution_time,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_delta=memory_delta,
                timestamp=time.time()
            )
            
            self.operations.append(operation_metadata)
            return result
        
        return wrapped_method
    
    def patch_pandas(self) -> None:
        """Patch pandas methods to enable tracing."""
        if not self.is_active:
            return
            
        # Store original methods
        self._original_methods = {
            'merge': pd.DataFrame.merge,
            'join': pd.DataFrame.join,
            'concat': pd.concat,
            'groupby': pd.DataFrame.groupby,
            'filter': pd.DataFrame.filter,
            'assign': pd.DataFrame.assign,
            'drop': pd.DataFrame.drop,
            'dropna': pd.DataFrame.dropna,
            'fillna': pd.DataFrame.fillna,
            'sort_values': pd.DataFrame.sort_values,
            'reset_index': pd.DataFrame.reset_index,
            'set_index': pd.DataFrame.set_index,
            'query': pd.DataFrame.query,
            'loc': pd.DataFrame.loc,
            'iloc': pd.DataFrame.iloc,
        }
        
        # Wrap methods
        pd.DataFrame.merge = self._wrap_method(pd.DataFrame.merge, 'merge')
        pd.DataFrame.join = self._wrap_method(pd.DataFrame.join, 'join')
        pd.concat = self._wrap_method(pd.concat, 'concat')
        pd.DataFrame.groupby = self._wrap_method(pd.DataFrame.groupby, 'groupby')
        pd.DataFrame.filter = self._wrap_method(pd.DataFrame.filter, 'filter')
        pd.DataFrame.assign = self._wrap_method(pd.DataFrame.assign, 'assign')
        pd.DataFrame.drop = self._wrap_method(pd.DataFrame.drop, 'drop')
        pd.DataFrame.dropna = self._wrap_method(pd.DataFrame.dropna, 'dropna')
        pd.DataFrame.fillna = self._wrap_method(pd.DataFrame.fillna, 'fillna')
        pd.DataFrame.sort_values = self._wrap_method(pd.DataFrame.sort_values, 'sort_values')
        pd.DataFrame.reset_index = self._wrap_method(pd.DataFrame.reset_index, 'reset_index')
        pd.DataFrame.set_index = self._wrap_method(pd.DataFrame.set_index, 'set_index')
        pd.DataFrame.query = self._wrap_method(pd.DataFrame.query, 'query')
        
    def unpatch_pandas(self) -> None:
        """Restore original pandas methods."""
        if self._original_methods:
            for method_name, original_method in self._original_methods.items():
                if method_name == 'concat':
                    pd.concat = original_method
                else:
                    setattr(pd.DataFrame, method_name, original_method)
            self._original_methods.clear()
    
    @contextmanager
    def trace_session(self):
        """Context manager for tracing sessions."""
        try:
            self.start_session()
            self.patch_pandas()
            yield self
        finally:
            self.unpatch_pandas()
            self.stop_session()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current tracing session."""
        if not self.operations:
            return {}
            
        total_operations = len(self.operations)
        total_execution_time = sum(op.execution_time for op in self.operations)
        total_memory_delta = sum(op.memory_delta for op in self.operations)
        
        operation_counts = {}
        for op in self.operations:
            operation_counts[op.operation_name] = operation_counts.get(op.operation_name, 0) + 1
        
        return {
            'session_id': self.session_id,
            'total_operations': total_operations,
            'total_execution_time': total_execution_time,
            'total_memory_delta': total_memory_delta,
            'operation_counts': operation_counts,
            'dataframe_count': len(self.dataframes)
        } 