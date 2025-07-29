"""
Performance analysis engine for tracking execution time and memory usage.
"""

import time
import psutil
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from ..utils.memory import get_memory_usage, get_system_memory_info
from ..utils.formatting import format_bytes, format_time


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    
    operation_id: str
    operation_name: str
    execution_time: float
    memory_before: int
    memory_after: int
    memory_delta: int
    cpu_percent: float
    timestamp: float
    
    @property
    def memory_delta_formatted(self) -> str:
        return format_bytes(self.memory_delta)
    
    @property
    def execution_time_formatted(self) -> str:
        return format_time(self.execution_time)


@dataclass
class PerformanceSummary:
    """Summary of performance metrics across all operations."""
    
    total_operations: int
    total_execution_time: float
    total_memory_delta: int
    average_execution_time: float
    average_memory_delta: int
    slowest_operation: Optional[PerformanceMetrics] = None
    memory_intensive_operation: Optional[PerformanceMetrics] = None
    bottlenecks: List[PerformanceMetrics] = None
    
    def __post_init__(self):
        if self.bottlenecks is None:
            self.bottlenecks = []
    
    @property
    def total_execution_time_formatted(self) -> str:
        return format_time(self.total_execution_time)
    
    @property
    def total_memory_delta_formatted(self) -> str:
        return format_bytes(self.total_memory_delta)
    
    @property
    def average_execution_time_formatted(self) -> str:
        return format_time(self.average_execution_time)
    
    @property
    def average_memory_delta_formatted(self) -> str:
        return format_bytes(self.average_memory_delta)


class PerformanceEngine:
    """
    Performance analysis engine for tracking execution time and memory usage.
    
    This class provides comprehensive performance monitoring capabilities
    including execution time tracking, memory profiling, and bottleneck detection.
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process(os.getpid())
        self.session_start_time = None
        self.session_start_memory = None
        
    def start_session(self) -> None:
        """Start a new performance monitoring session."""
        self.metrics.clear()
        self.session_start_time = time.time()
        self.session_start_memory = get_memory_usage(self.process)
    
    def stop_session(self) -> None:
        """Stop the current performance monitoring session."""
        self.session_start_time = None
        self.session_start_memory = None
    
    @contextmanager
    def monitor_operation(self, operation_id: str, operation_name: str):
        """
        Context manager for monitoring a single operation.
        
        Args:
            operation_id: Unique identifier for the operation.
            operation_name: Name of the operation.
            
        Yields:
            PerformanceMetrics object for the operation.
        """
        memory_before = get_memory_usage(self.process)
        cpu_before = self.process.cpu_percent()
        start_time = time.time()
        metrics = None
        try:
            yield lambda: metrics  # Provide a lambda to get the metrics after the block
        finally:
            end_time = time.time()
            memory_after = get_memory_usage(self.process)
            cpu_after = self.process.cpu_percent()
            metrics = PerformanceMetrics(
                operation_id=operation_id,
                operation_name=operation_name,
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_delta=memory_after - memory_before,
                cpu_percent=(cpu_before + cpu_after) / 2,
                timestamp=end_time
            )
            self.metrics.append(metrics)
    
    def record_operation(self, operation_id: str, operation_name: str,
                       execution_time: float, memory_before: int,
                       memory_after: int, memory_delta: int = None, cpu_percent: float = 0.0) -> None:
        """
        Record performance metrics for an operation.
        
        Args:
            operation_id: Unique identifier for the operation.
            operation_name: Name of the operation.
            execution_time: Execution time in seconds.
            memory_before: Memory usage before operation in bytes.
            memory_after: Memory usage after operation in bytes.
            memory_delta: Memory delta (optional, if not provided will be computed).
            cpu_percent: CPU usage percentage.
        """
        if memory_delta is None:
            memory_delta = memory_after - memory_before
        metrics = PerformanceMetrics(
            operation_id=operation_id,
            operation_name=operation_name,
            execution_time=execution_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_delta=memory_delta,
            cpu_percent=cpu_percent,
            timestamp=time.time()
        )
        self.metrics.append(metrics)
    
    def get_performance_summary(self) -> PerformanceSummary:
        """
        Get a summary of performance metrics.
        
        Returns:
            PerformanceSummary object with aggregated metrics.
        """
        if not self.metrics:
            return PerformanceSummary(
                total_operations=0,
                total_execution_time=0.0,
                total_memory_delta=0,
                average_execution_time=0.0,
                average_memory_delta=0
            )
        
        total_operations = len(self.metrics)
        total_execution_time = sum(m.execution_time for m in self.metrics)
        total_memory_delta = sum(m.memory_delta for m in self.metrics)
        average_execution_time = total_execution_time / total_operations
        average_memory_delta = total_memory_delta / total_operations
        
        # Find slowest operation
        slowest_operation = max(self.metrics, key=lambda m: m.execution_time)
        
        # Find most memory-intensive operation
        memory_intensive_operation = max(self.metrics, key=lambda m: abs(m.memory_delta))
        
        # Find bottlenecks (operations taking more than 1 second or using more than 100MB)
        bottlenecks = [
            m for m in self.metrics
            if m.execution_time > 1.0 or abs(m.memory_delta) > 100 * 1024 * 1024
        ]
        
        return PerformanceSummary(
            total_operations=total_operations,
            total_execution_time=total_execution_time,
            total_memory_delta=total_memory_delta,
            average_execution_time=average_execution_time,
            average_memory_delta=average_memory_delta,
            slowest_operation=slowest_operation,
            memory_intensive_operation=memory_intensive_operation,
            bottlenecks=bottlenecks
        )
    
    def get_operation_metrics(self, operation_id: str) -> Optional[PerformanceMetrics]:
        """
        Get metrics for a specific operation.
        
        Args:
            operation_id: ID of the operation to retrieve.
            
        Returns:
            PerformanceMetrics object if found, None otherwise.
        """
        for metrics in self.metrics:
            if metrics.operation_id == operation_id:
                return metrics
        return None
    
    def get_operation_by_name(self, operation_name: str) -> List[PerformanceMetrics]:
        """
        Get all metrics for operations with a specific name.
        
        Args:
            operation_name: Name of the operation to retrieve.
            
        Returns:
            List of PerformanceMetrics objects.
        """
        return [m for m in self.metrics if m.operation_name == operation_name]
    
    def find_bottlenecks(self, threshold_time: float = 1.0, 
                        threshold_memory: int = 100 * 1024 * 1024) -> List[PerformanceMetrics]:
        """
        Find performance bottlenecks.
        
        Args:
            threshold_time: Time threshold in seconds for slow operations.
            threshold_memory: Memory threshold in bytes for memory-intensive operations.
            
        Returns:
            List of bottleneck operations.
        """
        bottlenecks = []
        
        for metrics in self.metrics:
            if (metrics.execution_time > threshold_time or 
                abs(metrics.memory_delta) > threshold_memory):
                bottlenecks.append(metrics)
        
        return sorted(bottlenecks, key=lambda m: m.execution_time, reverse=True)
    
    def get_memory_trend(self) -> List[Tuple[float, int]]:
        """
        Get memory usage trend over time.
        
        Returns:
            List of (timestamp, memory_usage) tuples.
        """
        return [(m.timestamp, m.memory_after) for m in self.metrics]
    
    def get_execution_timeline(self) -> List[Tuple[float, float]]:
        """
        Get execution time timeline.
        
        Returns:
            List of (timestamp, execution_time) tuples.
        """
        return [(m.timestamp, m.execution_time) for m in self.metrics]
    
    def get_system_performance(self) -> Dict[str, Any]:
        """
        Get system-level performance information.
        
        Returns:
            Dictionary containing system performance metrics.
        """
        memory_info = get_system_memory_info()
        
        return {
            'system_memory': memory_info,
            'process_memory': get_memory_usage(self.process),
            'process_cpu': self.process.cpu_percent(),
            'session_duration': time.time() - self.session_start_time if self.session_start_time else 0,
            'session_memory_delta': (get_memory_usage(self.process) - self.session_start_memory 
                                   if self.session_start_memory else 0)
        }
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Export performance metrics in various formats.
        
        Args:
            format: Export format ('json', 'csv').
            
        Returns:
            String representation of the metrics.
        """
        if format == 'json':
            import json
            return json.dumps([m.__dict__ for m in self.metrics], indent=2)
        elif format == 'csv':
            import io
            import csv
            
            output = io.StringIO()
            if self.metrics:
                writer = csv.DictWriter(output, fieldnames=self.metrics[0].__dict__.keys())
                writer.writeheader()
                for metrics in self.metrics:
                    writer.writerow(metrics.__dict__)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary containing performance report.
        """
        summary = self.get_performance_summary()
        system_perf = self.get_system_performance()
        bottlenecks = self.find_bottlenecks()
        
        return {
            'summary': {
                'total_operations': summary.total_operations,
                'total_execution_time': summary.total_execution_time_formatted,
                'total_memory_delta': summary.total_memory_delta_formatted,
                'average_execution_time': summary.average_execution_time_formatted,
                'average_memory_delta': summary.average_memory_delta_formatted
            },
            'system_performance': system_perf,
            'bottlenecks': [
                {
                    'operation_name': b.operation_name,
                    'execution_time': b.execution_time_formatted,
                    'memory_delta': b.memory_delta_formatted,
                    'cpu_percent': b.cpu_percent
                }
                for b in bottlenecks
            ],
            'slowest_operation': {
                'name': summary.slowest_operation.operation_name,
                'time': summary.slowest_operation.execution_time_formatted
            } if summary.slowest_operation else None,
            'memory_intensive_operation': {
                'name': summary.memory_intensive_operation.operation_name,
                'memory_delta': summary.memory_intensive_operation.memory_delta_formatted
            } if summary.memory_intensive_operation else None
        } 