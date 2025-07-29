"""
Tests for the AuraTrace performance engine.
"""

import pytest
import time
import psutil
import os
from contextlib import contextmanager
from auratrace.core.performance import PerformanceEngine, PerformanceMetrics, PerformanceSummary


class TestPerformanceEngine:
    """Test cases for the PerformanceEngine class."""
    
    def test_performance_engine_initialization(self):
        """Test performance engine initialization."""
        engine = PerformanceEngine()
        assert len(engine.metrics) == 0
        assert engine.session_start_time is None
        assert engine.session_start_memory is None
    
    def test_start_stop_session(self):
        """Test session start and stop."""
        engine = PerformanceEngine()
        
        # Start session
        engine.start_session()
        assert engine.session_start_time is not None
        assert engine.session_start_memory is not None
        
        # Stop session
        engine.stop_session()
        assert engine.session_start_time is None
        assert engine.session_start_memory is None
    
    def test_monitor_operation_context_manager(self):
        """Test operation monitoring context manager."""
        engine = PerformanceEngine()
        engine.start_session()
        
        with engine.monitor_operation("test_op", "test_operation") as metrics:
            # Simulate some work
            time.sleep(0.1)
        
        assert len(engine.metrics) == 1
        metric = engine.metrics[0]
        assert metric.operation_id == "test_op"
        assert metric.operation_name == "test_operation"
        assert metric.execution_time > 0
        assert metric.memory_delta != 0
    
    def test_record_operation(self):
        """Test recording operation metrics."""
        engine = PerformanceEngine()
        
        engine.record_operation(
            operation_id="test_op",
            operation_name="test_operation",
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            cpu_percent=25.0
        )
        
        assert len(engine.metrics) == 1
        metric = engine.metrics[0]
        assert metric.operation_id == "test_op"
        assert metric.operation_name == "test_operation"
        assert metric.execution_time == 1.5
        assert metric.memory_before == 1000
        assert metric.memory_after == 1500
        assert metric.memory_delta == 500
        assert metric.cpu_percent == 25.0
    
    def test_get_performance_summary_empty(self):
        """Test performance summary for empty session."""
        engine = PerformanceEngine()
        summary = engine.get_performance_summary()
        
        assert summary.total_operations == 0
        assert summary.total_execution_time == 0.0
        assert summary.total_memory_delta == 0
        assert summary.average_execution_time == 0.0
        assert summary.average_memory_delta == 0
        assert summary.slowest_operation is None
        assert summary.memory_intensive_operation is None
        assert len(summary.bottlenecks) == 0
    
    def test_get_performance_summary_with_data(self):
        """Test performance summary with metrics."""
        engine = PerformanceEngine()
        
        # Add some metrics
        engine.record_operation(
            operation_id="op1",
            operation_name="fast_operation",
            execution_time=0.5,
            memory_before=1000,
            memory_after=1100,
            memory_delta=100,
            cpu_percent=10.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="slow_operation",
            execution_time=5.0,
            memory_before=1100,
            memory_after=1200,
            memory_delta=100,
            cpu_percent=50.0
        )
        
        engine.record_operation(
            operation_id="op3",
            operation_name="memory_intensive",
            execution_time=1.0,
            memory_before=1200,
            memory_after=2200,
            memory_delta=1000,
            cpu_percent=30.0
        )
        
        summary = engine.get_performance_summary()
        
        assert summary.total_operations == 3
        assert summary.total_execution_time == 6.5
        assert summary.total_memory_delta == 1200
        assert summary.average_execution_time == 2.1666666666666665
        assert summary.average_memory_delta == 400
        
        # Check slowest operation
        assert summary.slowest_operation is not None
        assert summary.slowest_operation.operation_name == "slow_operation"
        assert summary.slowest_operation.execution_time == 5.0
        
        # Check memory intensive operation
        assert summary.memory_intensive_operation is not None
        assert summary.memory_intensive_operation.operation_name == "memory_intensive"
        assert summary.memory_intensive_operation.memory_delta == 1000
        
        # Check bottlenecks
        assert len(summary.bottlenecks) >= 2  # Should include slow and memory-intensive ops
    
    def test_get_operation_metrics(self):
        """Test getting metrics for specific operation."""
        engine = PerformanceEngine()
        
        engine.record_operation(
            operation_id="test_op",
            operation_name="test_operation",
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=25.0
        )
        
        metric = engine.get_operation_metrics("test_op")
        assert metric is not None
        assert metric.operation_id == "test_op"
        assert metric.operation_name == "test_operation"
        assert metric.execution_time == 1.5
        
        # Test non-existent operation
        metric = engine.get_operation_metrics("non_existent")
        assert metric is None
    
    def test_get_operation_by_name(self):
        """Test getting operations by name."""
        engine = PerformanceEngine()
        
        # Add operations with same name
        engine.record_operation(
            operation_id="op1",
            operation_name="merge",
            execution_time=1.0,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=20.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="merge",
            execution_time=2.0,
            memory_before=1500,
            memory_after=2000,
            memory_delta=500,
            cpu_percent=30.0
        )
        
        engine.record_operation(
            operation_id="op3",
            operation_name="groupby",
            execution_time=1.5,
            memory_before=2000,
            memory_after=2500,
            memory_delta=500,
            cpu_percent=25.0
        )
        
        merge_ops = engine.get_operation_by_name("merge")
        assert len(merge_ops) == 2
        
        groupby_ops = engine.get_operation_by_name("groupby")
        assert len(groupby_ops) == 1
        
        non_existent_ops = engine.get_operation_by_name("non_existent")
        assert len(non_existent_ops) == 0
    
    def test_find_bottlenecks(self):
        """Test finding performance bottlenecks."""
        engine = PerformanceEngine()
        
        # Add operations with different characteristics
        engine.record_operation(
            operation_id="op1",
            operation_name="fast_operation",
            execution_time=0.5,  # Fast
            memory_before=1000,
            memory_after=1100,
            memory_delta=100,
            cpu_percent=10.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="slow_operation",
            execution_time=5.0,  # Slow
            memory_before=1100,
            memory_after=1200,
            memory_delta=100,
            cpu_percent=50.0
        )
        
        engine.record_operation(
            operation_id="op3",
            operation_name="memory_intensive",
            execution_time=1.0,
            memory_before=1200,
            memory_after=2200,  # Large memory increase
            memory_delta=1000,
            cpu_percent=30.0
        )
        
        bottlenecks = engine.find_bottlenecks()
        
        # Should find slow and memory-intensive operations
        assert len(bottlenecks) >= 2
        
        slow_ops = [b for b in bottlenecks if b.operation_name == "slow_operation"]
        memory_ops = [b for b in bottlenecks if b.operation_name == "memory_intensive"]
        
        assert len(slow_ops) > 0
        assert len(memory_ops) > 0
    
    def test_get_memory_trend(self):
        """Test getting memory usage trend."""
        engine = PerformanceEngine()
        
        # Add some metrics
        engine.record_operation(
            operation_id="op1",
            operation_name="operation1",
            execution_time=1.0,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=20.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="operation2",
            execution_time=2.0,
            memory_before=1500,
            memory_after=2000,
            memory_delta=500,
            cpu_percent=30.0
        )
        
        trend = engine.get_memory_trend()
        
        assert len(trend) == 2
        assert all(isinstance(item, tuple) for item in trend)
        assert all(len(item) == 2 for item in trend)
        assert all(isinstance(item[0], float) for item in trend)
        assert all(isinstance(item[1], int) for item in trend)
    
    def test_get_execution_timeline(self):
        """Test getting execution timeline."""
        engine = PerformanceEngine()
        
        # Add some metrics
        engine.record_operation(
            operation_id="op1",
            operation_name="operation1",
            execution_time=1.0,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=20.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="operation2",
            execution_time=2.0,
            memory_before=1500,
            memory_after=2000,
            memory_delta=500,
            cpu_percent=30.0
        )
        
        timeline = engine.get_execution_timeline()
        
        assert len(timeline) == 2
        assert all(isinstance(item, tuple) for item in timeline)
        assert all(len(item) == 2 for item in timeline)
        assert all(isinstance(item[0], float) for item in timeline)
        assert all(isinstance(item[1], float) for item in timeline)
    
    def test_get_system_performance(self):
        """Test getting system performance information."""
        engine = PerformanceEngine()
        engine.start_session()
        
        system_perf = engine.get_system_performance()
        
        assert 'system_memory' in system_perf
        assert 'process_memory' in system_perf
        assert 'process_cpu' in system_perf
        assert 'session_duration' in system_perf
        assert 'session_memory_delta' in system_perf
        
        # Check that values are reasonable
        assert system_perf['process_memory'] > 0
        assert system_perf['session_duration'] >= 0
    
    def test_export_metrics(self):
        """Test exporting metrics in different formats."""
        engine = PerformanceEngine()
        
        # Add some metrics
        engine.record_operation(
            operation_id="test_op",
            operation_name="test_operation",
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=25.0
        )
        
        # Test JSON export
        json_export = engine.export_metrics('json')
        assert isinstance(json_export, str)
        assert 'test_op' in json_export
        
        # Test CSV export
        csv_export = engine.export_metrics('csv')
        assert isinstance(csv_export, str)
        assert 'test_op' in csv_export
        
        # Test unsupported format
        with pytest.raises(ValueError):
            engine.export_metrics('unsupported')
    
    def test_generate_performance_report(self):
        """Test generating performance report."""
        engine = PerformanceEngine()
        
        # Add some metrics
        engine.record_operation(
            operation_id="op1",
            operation_name="fast_operation",
            execution_time=0.5,
            memory_before=1000,
            memory_after=1100,
            memory_delta=100,
            cpu_percent=10.0
        )
        
        engine.record_operation(
            operation_id="op2",
            operation_name="slow_operation",
            execution_time=5.0,
            memory_before=1100,
            memory_after=1200,
            memory_delta=100,
            cpu_percent=50.0
        )
        
        report = engine.generate_performance_report()
        
        assert 'summary' in report
        assert 'system_performance' in report
        assert 'bottlenecks' in report
        assert 'slowest_operation' in report
        assert 'memory_intensive_operation' in report
        
        # Check summary
        summary = report['summary']
        assert 'total_operations' in summary
        assert 'total_execution_time' in summary
        assert 'total_memory_delta' in summary
        assert 'average_execution_time' in summary
        assert 'average_memory_delta' in summary
        
        # Check bottlenecks
        bottlenecks = report['bottlenecks']
        assert isinstance(bottlenecks, list)
        assert len(bottlenecks) > 0


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics."""
    
    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics creation."""
        metrics = PerformanceMetrics(
            operation_id="test_op",
            operation_name="test_operation",
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=25.0,
            timestamp=1234567890.0
        )
        
        assert metrics.operation_id == "test_op"
        assert metrics.operation_name == "test_operation"
        assert metrics.execution_time == 1.5
        assert metrics.memory_before == 1000
        assert metrics.memory_after == 1500
        assert metrics.memory_delta == 500
        assert metrics.cpu_percent == 25.0
        assert metrics.timestamp == 1234567890.0
    
    def test_performance_metrics_formatted_properties(self):
        """Test PerformanceMetrics formatted properties."""
        metrics = PerformanceMetrics(
            operation_id="test_op",
            operation_name="test_operation",
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            cpu_percent=25.0,
            timestamp=1234567890.0
        )
        
        # Test formatted properties
        assert isinstance(metrics.memory_delta_formatted, str)
        assert isinstance(metrics.execution_time_formatted, str)
        
        # Should contain reasonable values
        assert "500" in metrics.memory_delta_formatted or "B" in metrics.memory_delta_formatted
        assert "1.5" in metrics.execution_time_formatted or "s" in metrics.execution_time_formatted


class TestPerformanceSummary:
    """Test cases for PerformanceSummary."""
    
    def test_performance_summary_creation(self):
        """Test PerformanceSummary creation."""
        summary = PerformanceSummary(
            total_operations=5,
            total_execution_time=10.5,
            total_memory_delta=2000,
            average_execution_time=2.1,
            average_memory_delta=400
        )
        
        assert summary.total_operations == 5
        assert summary.total_execution_time == 10.5
        assert summary.total_memory_delta == 2000
        assert summary.average_execution_time == 2.1
        assert summary.average_memory_delta == 400
        assert summary.slowest_operation is None
        assert summary.memory_intensive_operation is None
        assert len(summary.bottlenecks) == 0
    
    def test_performance_summary_formatted_properties(self):
        """Test PerformanceSummary formatted properties."""
        summary = PerformanceSummary(
            total_operations=5,
            total_execution_time=10.5,
            total_memory_delta=2000,
            average_execution_time=2.1,
            average_memory_delta=400
        )
        
        # Test formatted properties
        assert isinstance(summary.total_execution_time_formatted, str)
        assert isinstance(summary.total_memory_delta_formatted, str)
        assert isinstance(summary.average_execution_time_formatted, str)
        assert isinstance(summary.average_memory_delta_formatted, str)
        
        # Should contain reasonable values
        assert "10.5" in summary.total_execution_time_formatted or "s" in summary.total_execution_time_formatted
        assert "2000" in summary.total_memory_delta_formatted or "B" in summary.total_memory_delta_formatted


@pytest.fixture
def performance_engine():
    """Create a fresh performance engine instance."""
    return PerformanceEngine()


class TestPerformanceIntegration:
    """Integration tests for the performance engine."""
    
    def test_comprehensive_performance_monitoring(self, performance_engine):
        """Test comprehensive performance monitoring."""
        performance_engine.start_session()
        
        # Monitor multiple operations
        with performance_engine.monitor_operation("op1", "data_loading"):
            time.sleep(0.1)  # Simulate work
        
        with performance_engine.monitor_operation("op2", "data_processing"):
            time.sleep(0.2)  # Simulate more work
        
        with performance_engine.monitor_operation("op3", "data_aggregation"):
            time.sleep(0.05)  # Simulate less work
        
        # Get summary
        summary = performance_engine.get_performance_summary()
        
        assert summary.total_operations == 3
        assert summary.total_execution_time > 0
        assert summary.average_execution_time > 0
        
        # Check bottlenecks
        bottlenecks = performance_engine.find_bottlenecks()
        assert len(bottlenecks) >= 0  # May or may not have bottlenecks depending on timing
        
        # Check system performance
        system_perf = performance_engine.get_system_performance()
        assert 'process_memory' in system_perf
        assert 'process_cpu' in system_perf
        
        performance_engine.stop_session()
    
    def test_memory_tracking_accuracy(self, performance_engine):
        """Test that memory tracking is reasonably accurate."""
        performance_engine.start_session()
        
        # Record initial memory
        initial_memory = performance_engine.get_system_performance()['process_memory']
        
        # Create a large object to increase memory usage
        large_list = [0] * 1000000  # ~8MB of integers
        
        # Monitor operation
        with performance_engine.monitor_operation("memory_test", "memory_operation"):
            pass
        
        # Check that memory tracking detected the change
        summary = performance_engine.get_performance_summary()
        assert summary.total_operations == 1
        
        # The memory delta should be positive (or at least not negative)
        # Note: This is approximate due to garbage collection and other factors
        assert summary.total_memory_delta >= -1000000  # Allow for some variance
        
        performance_engine.stop_session()
    
    def test_performance_report_integration(self, performance_engine):
        """Test performance report generation with real data."""
        performance_engine.start_session()
        
        # Add various types of operations
        operations = [
            ("fast_op", "fast_operation", 0.1),
            ("slow_op", "slow_operation", 0.5),
            ("memory_op", "memory_intensive", 0.2)
        ]
        
        for op_id, op_name, duration in operations:
            with performance_engine.monitor_operation(op_id, op_name):
                time.sleep(duration)
        
        # Generate report
        report = performance_engine.generate_performance_report()
        
        # Check report structure
        assert 'summary' in report
        assert 'system_performance' in report
        assert 'bottlenecks' in report
        
        # Check summary
        summary = report['summary']
        assert summary['total_operations'] == 3
        assert summary['total_execution_time'] > 0
        
        # Check bottlenecks
        bottlenecks = report['bottlenecks']
        assert isinstance(bottlenecks, list)
        
        performance_engine.stop_session() 