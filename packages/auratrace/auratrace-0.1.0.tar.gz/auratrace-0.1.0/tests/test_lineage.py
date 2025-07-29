"""
Tests for the AuraTrace lineage engine.
"""

import pytest
import pandas as pd
import networkx as nx
from unittest.mock import Mock

from auratrace.core.lineage import LineageEngine, LineageNode, LineageEdge
from auratrace.core.tracer import OperationMetadata, DataframeMetadata


class TestLineageEngine:
    """Test cases for the LineageEngine class."""
    
    def test_lineage_engine_initialization(self):
        """Test lineage engine initialization."""
        engine = LineageEngine()
        assert isinstance(engine.graph, nx.DiGraph)
        assert len(engine.nodes) == 0
        assert len(engine.edges) == 0
    
    def test_build_lineage_graph_empty(self):
        """Test building lineage graph with empty data."""
        engine = LineageEngine()
        operations = []
        dataframes = {}
        
        graph = engine.build_lineage_graph(operations, dataframes)
        
        assert isinstance(graph, nx.DiGraph)
        assert len(graph.nodes()) == 0
        assert len(graph.edges()) == 0
    
    def test_build_lineage_graph_with_data(self):
        """Test building lineage graph with sample data."""
        engine = LineageEngine()
        
        # Create sample operations
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1", "df2"],
                output_ids=["df3", "df5"],  # two outputs
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            ),
            OperationMetadata(
                operation_id="op2",
                operation_name="groupby",
                input_ids=["df3"],
                output_ids=["df4", "df6"],  # two outputs
                parameters={},
                execution_time=2.0,
                memory_before=1500,
                memory_after=2000,
                memory_delta=500,
                timestamp=1234567891.0
            )
        ]
        
        # Create sample dataframes
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3), "columns": ["A", "B", "C"]},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (50, 2), "columns": ["A", "D"]},
                row_count=50,
                column_count=2,
                memory_usage=512,
                timestamp=1234567889.0
            ),
            "df3": DataframeMetadata(
                dataframe_id="df3",
                dataframe_hash="hash3",
                schema={"shape": (80, 4), "columns": ["A", "B", "C", "D"]},
                row_count=80,
                column_count=4,
                memory_usage=1536,
                timestamp=1234567890.0
            ),
            "df4": DataframeMetadata(
                dataframe_id="df4",
                dataframe_hash="hash4",
                schema={"shape": (3, 2), "columns": ["category", "count"]},
                row_count=3,
                column_count=2,
                memory_usage=256,
                timestamp=1234567891.0
            ),
            "df5": DataframeMetadata(
                dataframe_id="df5",
                dataframe_hash="hash5",
                schema={"shape": (10, 2), "columns": ["E", "F"]},
                row_count=10,
                column_count=2,
                memory_usage=128,
                timestamp=1234567890.5
            ),
            "df6": DataframeMetadata(
                dataframe_id="df6",
                dataframe_hash="hash6",
                schema={"shape": (5, 1), "columns": ["G"]},
                row_count=5,
                column_count=1,
                memory_usage=64,
                timestamp=1234567891.5
            )
        }
        
        graph = engine.build_lineage_graph(operations, dataframes)
        
        # Check that graph was built correctly
        assert len(graph.nodes()) == 8  # 6 dataframes + 2 operations
        assert len(graph.edges()) == 8  # 2 inputs + 2 outputs for each operation
        
        # Check that nodes exist
        assert "df1" in graph.nodes()
        assert "df2" in graph.nodes()
        assert "df3" in graph.nodes()
        assert "df4" in graph.nodes()
        assert "df5" in graph.nodes()
        assert "df6" in graph.nodes()
        assert "op_op1" in graph.nodes()
        assert "op_op2" in graph.nodes()
    
    def test_get_dataframe_lineage(self):
        """Test getting lineage for a specific dataframe."""
        engine = LineageEngine()
        
        # Build a simple lineage graph
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1", "df2"],
                output_ids=["df3"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (50, 2)},
                row_count=50,
                column_count=2,
                memory_usage=512,
                timestamp=1234567889.0
            ),
            "df3": DataframeMetadata(
                dataframe_id="df3",
                dataframe_hash="hash3",
                schema={"shape": (80, 4)},
                row_count=80,
                column_count=4,
                memory_usage=1536,
                timestamp=1234567890.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        # Get lineage for df3
        lineage = engine.get_dataframe_lineage("df3")
        
        assert lineage['dataframe_id'] == "df3"
        assert "df1" in lineage['ancestors']
        assert "df2" in lineage['ancestors']
        assert "op_op1" in lineage['predecessors']
        assert lineage['ancestor_count'] == 2
        assert lineage['descendant_count'] == 0
    
    def test_get_operation_impact(self):
        """Test getting impact of a specific operation."""
        engine = LineageEngine()
        
        # Build a lineage graph
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1", "df2"],
                output_ids=["df3"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            ),
            OperationMetadata(
                operation_id="op2",
                operation_name="groupby",
                input_ids=["df3"],
                output_ids=["df4"],
                parameters={},
                execution_time=2.0,
                memory_before=1500,
                memory_after=2000,
                memory_delta=500,
                timestamp=1234567891.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (50, 2)},
                row_count=50,
                column_count=2,
                memory_usage=512,
                timestamp=1234567889.0
            ),
            "df3": DataframeMetadata(
                dataframe_id="df3",
                dataframe_hash="hash3",
                schema={"shape": (80, 4)},
                row_count=80,
                column_count=4,
                memory_usage=1536,
                timestamp=1234567890.0
            ),
            "df4": DataframeMetadata(
                dataframe_id="df4",
                dataframe_hash="hash4",
                schema={"shape": (3, 2)},
                row_count=3,
                column_count=2,
                memory_usage=256,
                timestamp=1234567891.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        # Get impact of op1
        impact = engine.get_operation_impact("op1")
        
        assert impact['operation_id'] == "op1"
        assert impact['operation_name'] == "merge"
        assert "df3" in impact['affected_dataframes']
        assert "df4" in impact['affected_dataframes']
        assert impact['affected_count'] == 2
        assert impact['execution_time'] == 1.0
        assert impact['memory_delta'] == 500
    
    def test_find_bottlenecks(self):
        """Test finding performance bottlenecks."""
        engine = LineageEngine()
        
        # Create operations with different performance characteristics
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="fast_operation",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=0.5,  # Fast
                memory_before=1000,
                memory_after=1100,
                memory_delta=100,
                timestamp=1234567890.0
            ),
            OperationMetadata(
                operation_id="op2",
                operation_name="slow_operation",
                input_ids=["df2"],
                output_ids=["df3"],
                parameters={},
                execution_time=5.0,  # Slow
                memory_before=1100,
                memory_after=1200,
                memory_delta=100,
                timestamp=1234567891.0
            ),
            OperationMetadata(
                operation_id="op3",
                operation_name="memory_intensive",
                input_ids=["df3"],
                output_ids=["df4"],
                parameters={},
                execution_time=1.0,
                memory_before=1200,
                memory_after=2200,  # Large memory increase
                memory_delta=1000,
                timestamp=1234567892.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            ),
            "df3": DataframeMetadata(
                dataframe_id="df3",
                dataframe_hash="hash3",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567891.0
            ),
            "df4": DataframeMetadata(
                dataframe_id="df4",
                dataframe_hash="hash4",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567892.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        bottlenecks = engine.find_bottlenecks()
        
        # Should find slow and memory-intensive operations
        assert len(bottlenecks) >= 2
        
        # Check for slow operation
        slow_ops = [b for b in bottlenecks if b['type'] == 'slow_operation']
        assert len(slow_ops) > 0
        
        # Check for memory-intensive operation
        memory_ops = [b for b in bottlenecks if b['type'] == 'memory_intensive']
        assert len(memory_ops) > 0
    
    def test_get_graph_summary(self):
        """Test getting graph summary."""
        engine = LineageEngine()
        
        # Build a simple graph
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        summary = engine.get_graph_summary()
        
        assert summary['total_nodes'] == 3  # 2 dataframes + 1 operation
        assert summary['total_edges'] == 2  # 1 input + 1 output
        assert summary['dataframe_nodes'] == 2
        assert summary['operation_nodes'] == 1
        assert summary['is_dag'] == True
        assert summary['has_cycles'] == False
        assert 'bottlenecks' in summary
    
    def test_export_graph(self):
        """Test graph export functionality."""
        engine = LineageEngine()
        
        # Build a simple graph
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        # Test JSON export
        json_export = engine.export_graph('json')
        assert isinstance(json_export, str)
        assert 'nodes' in json_export
        assert 'edges' in json_export
        
        # Test DOT export
        dot_export = engine.export_graph('dot')
        assert isinstance(dot_export, str)
        assert 'digraph' in dot_export
        
        # Test GML export
        gml_export = engine.export_graph('gml')
        assert isinstance(gml_export, str)
        assert 'graph' in gml_export
    
    def test_visualize_graph(self):
        """Test graph visualization."""
        engine = LineageEngine()
        
        # Build a simple graph
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        # Test visualization
        html_content = engine.visualize_graph()
        assert isinstance(html_content, str)
        assert 'html' in html_content.lower() or 'pyvis not available' in html_content
    
    def test_get_operation_chain(self):
        """Test getting operation chain between dataframes."""
        engine = LineageEngine()
        
        # Build a chain: df1 -> op1 -> df2 -> op2 -> df3
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            ),
            OperationMetadata(
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
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            ),
            "df3": DataframeMetadata(
                dataframe_id="df3",
                dataframe_hash="hash3",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567891.0
            )
        }
        
        engine.build_lineage_graph(operations, dataframes)
        
        # Get chain from df1 to df3
        chain = engine.get_operation_chain("df1", "df3")
        
        assert len(chain) == 2
        assert "op_op1" in chain
        assert "op_op2" in chain


class TestLineageNode:
    """Test cases for LineageNode."""
    
    def test_lineage_node_creation(self):
        """Test LineageNode creation."""
        node = LineageNode(
            node_id="test_node",
            node_type="dataframe",
            metadata={"shape": (100, 3)},
            timestamp=1234567890.0
        )
        
        assert node.node_id == "test_node"
        assert node.node_type == "dataframe"
        assert node.metadata["shape"] == (100, 3)
        assert node.timestamp == 1234567890.0


class TestLineageEdge:
    """Test cases for LineageEdge."""
    
    def test_lineage_edge_creation(self):
        """Test LineageEdge creation."""
        edge = LineageEdge(
            source_id="df1",
            target_id="df2",
            edge_type="transforms",
            metadata={"operation": "merge"}
        )
        
        assert edge.source_id == "df1"
        assert edge.target_id == "df2"
        assert edge.edge_type == "transforms"
        assert edge.metadata["operation"] == "merge"


@pytest.fixture
def sample_operations():
    """Create sample operations for testing."""
    return [
        OperationMetadata(
            operation_id="op1",
            operation_name="merge",
            input_ids=["df1", "df2"],
            output_ids=["df3", "df5"],  # two outputs
            parameters={"on": "id"},
            execution_time=1.5,
            memory_before=1000,
            memory_after=1500,
            memory_delta=500,
            timestamp=1234567890.0
        ),
        OperationMetadata(
            operation_id="op2",
            operation_name="groupby",
            input_ids=["df3"],
            output_ids=["df4", "df6"],  # two outputs
            parameters={"by": "category"},
            execution_time=2.0,
            memory_before=1500,
            memory_after=2000,
            memory_delta=500,
            timestamp=1234567891.0
        )
    ]


@pytest.fixture
def sample_dataframes():
    """Create sample dataframes for testing."""
    return {
        "df1": DataframeMetadata(
            dataframe_id="df1",
            dataframe_hash="hash1",
            schema={"shape": (100, 3), "columns": ["id", "name", "value"]},
            row_count=100,
            column_count=3,
            memory_usage=1024,
            timestamp=1234567889.0
        ),
        "df2": DataframeMetadata(
            dataframe_id="df2",
            dataframe_hash="hash2",
            schema={"shape": (50, 2), "columns": ["id", "category"]},
            row_count=50,
            column_count=2,
            memory_usage=512,
            timestamp=1234567889.0
        ),
        "df3": DataframeMetadata(
            dataframe_id="df3",
            dataframe_hash="hash3",
            schema={"shape": (80, 4), "columns": ["id", "name", "value", "category"]},
            row_count=80,
            column_count=4,
            memory_usage=1536,
            timestamp=1234567890.0
        ),
        "df4": DataframeMetadata(
            dataframe_id="df4",
            dataframe_hash="hash4",
            schema={"shape": (3, 2), "columns": ["category", "count"]},
            row_count=3,
            column_count=2,
            memory_usage=256,
            timestamp=1234567891.0
        ),
        "df5": DataframeMetadata(
            dataframe_id="df5",
            dataframe_hash="hash5",
            schema={"shape": (10, 2), "columns": ["E", "F"]},
            row_count=10,
            column_count=2,
            memory_usage=128,
            timestamp=1234567890.5
        ),
        "df6": DataframeMetadata(
            dataframe_id="df6",
            dataframe_hash="hash6",
            schema={"shape": (5, 1), "columns": ["G"]},
            row_count=5,
            column_count=1,
            memory_usage=64,
            timestamp=1234567891.5
        )
    }


@pytest.fixture
def lineage_engine():
    """Create a fresh lineage engine instance."""
    return LineageEngine()


class TestLineageIntegration:
    """Integration tests for the lineage engine."""
    
    def test_complex_lineage_analysis(self, lineage_engine, sample_operations, sample_dataframes):
        """Test complex lineage analysis."""
        # Build lineage graph
        graph = lineage_engine.build_lineage_graph(sample_operations, sample_dataframes)
        
        # Test graph properties
        assert len(graph.nodes()) == 8  # 6 dataframes + 2 operations
        assert len(graph.edges()) == 8  # 2 inputs + 2 outputs for each operation
        
        # Test lineage queries
        df3_lineage = lineage_engine.get_dataframe_lineage("df3")
        assert len(df3_lineage['ancestors']) == 2  # df1 and df2
        assert len(df3_lineage['descendants']) == 1  # df4
        
        # Test operation impact
        op1_impact = lineage_engine.get_operation_impact("op1")
        assert op1_impact['affected_count'] == 2  # df3 and df4
        
        # Test bottlenecks
        bottlenecks = lineage_engine.find_bottlenecks()
        assert len(bottlenecks) > 0
        
        # Test graph summary
        summary = lineage_engine.get_graph_summary()
        assert summary['total_nodes'] == 8
        assert summary['is_dag'] == True
    
    def test_cycle_detection(self, lineage_engine):
        """Test detection of cycles in lineage graph."""
        # Create operations that would create a cycle
        operations = [
            OperationMetadata(
                operation_id="op1",
                operation_name="merge",
                input_ids=["df1"],
                output_ids=["df2"],
                parameters={},
                execution_time=1.0,
                memory_before=1000,
                memory_after=1500,
                memory_delta=500,
                timestamp=1234567890.0
            ),
            OperationMetadata(
                operation_id="op2",
                operation_name="merge",
                input_ids=["df2"],
                output_ids=["df1"],  # This creates a cycle
                parameters={},
                execution_time=1.0,
                memory_before=1500,
                memory_after=2000,
                memory_delta=500,
                timestamp=1234567891.0
            )
        ]
        
        dataframes = {
            "df1": DataframeMetadata(
                dataframe_id="df1",
                dataframe_hash="hash1",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567889.0
            ),
            "df2": DataframeMetadata(
                dataframe_id="df2",
                dataframe_hash="hash2",
                schema={"shape": (100, 3)},
                row_count=100,
                column_count=3,
                memory_usage=1024,
                timestamp=1234567890.0
            )
        }
        
        graph = lineage_engine.build_lineage_graph(operations, dataframes)
        summary = lineage_engine.get_graph_summary()
        
        # Should detect the cycle
        assert summary['has_cycles'] == True
        assert summary['is_dag'] == False 