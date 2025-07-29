"""
AuraTrace lineage engine for building and analyzing data lineage graphs.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import networkx as nx

try:
    import pyvis
    from pyvis import network
    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False

from auratrace.core.tracer import OperationMetadata, DataframeMetadata


@dataclass
class LineageNode:
    """Represents a node in the lineage graph."""
    node_id: str
    node_type: str  # 'dataframe' or 'operation'
    metadata: Dict[str, Any]
    timestamp: float


@dataclass
class LineageEdge:
    """Represents an edge in the lineage graph."""
    source_id: str
    target_id: str
    edge_type: str  # 'transforms', 'depends_on', etc.
    metadata: Dict[str, Any]


class LineageEngine:
    """
    Engine for building and analyzing data lineage graphs.
    
    The lineage engine creates a directed acyclic graph (DAG) representing
    the flow of data through operations, enabling impact analysis and
    dependency tracking.
    """
    
    def __init__(self):
        """Initialize the lineage engine."""
        self.graph = nx.MultiDiGraph()
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
    
    def build_lineage_graph(
        self, 
        operations: List[OperationMetadata], 
        dataframes: Dict[str, DataframeMetadata]
    ) -> nx.DiGraph:
        """
        Build a lineage graph from operations and dataframes.
        
        Args:
            operations: List of operation metadata
            dataframes: Dictionary of dataframe metadata
            
        Returns:
            NetworkX DiGraph representing the lineage
        """
        # Clear existing graph
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
        
        # Add dataframe nodes
        for df_id, df_meta in dataframes.items():
            node = LineageNode(
                node_id=df_id,
                node_type='dataframe',
                metadata={
                    'shape': df_meta.schema.get('shape', (0, 0)),
                    'columns': df_meta.schema.get('columns', []),
                    'row_count': df_meta.row_count,
                    'column_count': df_meta.column_count,
                    'memory_usage': df_meta.memory_usage
                },
                timestamp=df_meta.timestamp
            )
            self.nodes[df_id] = node
            self.graph.add_node(df_id, **asdict(node))
        
        # Add operation nodes and edges
        for op in operations:
            op_node_id = f"op_{op.operation_id}"
            
            # Add operation node
            op_node = LineageNode(
                node_id=op_node_id,
                node_type='operation',
                metadata={
                    'operation_name': op.operation_name,
                    'execution_time': op.execution_time,
                    'memory_delta': op.memory_delta,
                    'parameters': op.parameters
                },
                timestamp=op.timestamp
            )
            self.nodes[op_node_id] = op_node
            self.graph.add_node(op_node_id, **asdict(op_node))
            
            # Ensure all input/output nodes exist in the graph
            for input_id in op.input_ids:
                if input_id not in self.graph.nodes:
                    # Add minimal node for missing input
                    self.graph.add_node(input_id, node_id=input_id, node_type='dataframe', metadata={}, timestamp=0)
            for output_id in op.output_ids:
                if output_id not in self.graph.nodes:
                    # Add minimal node for missing output
                    self.graph.add_node(output_id, node_id=output_id, node_type='dataframe', metadata={}, timestamp=0)
            
            # Add input edges (dataframes -> operation)
            for input_id in op.input_ids:
                edge = LineageEdge(
                    source_id=input_id,
                    target_id=op_node_id,
                    edge_type='transforms',
                    metadata={'operation': op.operation_name}
                )
                self.edges.append(edge)
                self.graph.add_edge(input_id, op_node_id, **asdict(edge))
            
            # Add output edges (operation -> dataframes)
            for output_id in op.output_ids:
                edge = LineageEdge(
                    source_id=op_node_id,
                    target_id=output_id,
                    edge_type='produces',
                    metadata={'operation': op.operation_name}
                )
                self.edges.append(edge)
                # Always add the edge, even if it already exists
                self.graph.add_edge(op_node_id, output_id, **asdict(edge))
        
        return self.graph
    
    def get_dataframe_lineage(self, dataframe_id: str) -> Dict[str, Any]:
        """
        Get lineage information for a specific dataframe.
        
        Args:
            dataframe_id: ID of the dataframe
            
        Returns:
            Dictionary with lineage information
        """
        if dataframe_id not in self.graph.nodes:
            return {}
        
        # Get ancestors (dataframes that this dataframe depends on)
        ancestors = list(nx.ancestors(self.graph, dataframe_id))
        ancestor_dataframes = [n for n in ancestors if not n.startswith('op_')]
        
        # Get descendants (dataframes that depend on this dataframe)
        descendants = list(nx.descendants(self.graph, dataframe_id))
        descendant_dataframes = [n for n in descendants if not n.startswith('op_')]
        
        # Get predecessor operations
        predecessors = [n for n in ancestors if n.startswith('op_')]
        
        return {
            'dataframe_id': dataframe_id,
            'ancestors': ancestor_dataframes,
            'descendants': descendant_dataframes,
            'predecessors': predecessors,
            'ancestor_count': len(ancestor_dataframes),
            'descendant_count': len(descendant_dataframes)
        }
    
    def get_operation_impact(self, operation_id: str) -> Dict[str, Any]:
        """
        Get impact analysis for a specific operation.
        
        Args:
            operation_id: ID of the operation
            
        Returns:
            Dictionary with impact information
        """
        op_node_id = f"op_{operation_id}"
        if op_node_id not in self.graph.nodes:
            return {}
        
        # Get all affected dataframes (descendants)
        descendants = list(nx.descendants(self.graph, op_node_id))
        affected_dataframes = [n for n in descendants if not n.startswith('op_')]
        
        # Get operation metadata
        op_metadata = self.nodes.get(op_node_id, {})
        
        return {
            'operation_id': operation_id,
            'operation_name': op_metadata.metadata.get('operation_name', ''),
            'affected_dataframes': affected_dataframes,
            'affected_count': len(affected_dataframes),
            'execution_time': op_metadata.metadata.get('execution_time', 0),
            'memory_delta': op_metadata.metadata.get('memory_delta', 0)
        }
    
    def find_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Find performance bottlenecks in the lineage graph.
        
        Returns:
            List of bottleneck information
        """
        bottlenecks = []
        
        # Find slow operations
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'operation':
                execution_time = node_data.get('metadata', {}).get('execution_time', 0)
                if execution_time >= 5.0:  # Threshold for slow operations (inclusive)
                    bottlenecks.append({
                        'type': 'slow_operation',
                        'node_id': node_id,
                        'operation_name': node_data.get('metadata', {}).get('operation_name', ''),
                        'execution_time': execution_time,
                        'severity': 'high' if execution_time > 10.0 else 'medium'
                    })
        
        # Find memory-intensive operations
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'operation':
                memory_delta = node_data.get('metadata', {}).get('memory_delta', 0)
                if memory_delta >= 1000:  # 1KB threshold (inclusive)
                    bottlenecks.append({
                        'type': 'memory_intensive',
                        'node_id': node_id,
                        'operation_name': node_data.get('metadata', {}).get('operation_name', ''),
                        'memory_delta': memory_delta,
                        'severity': 'high' if memory_delta > 10000000 else 'medium'
                    })
        
        return bottlenecks
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the lineage graph.
        
        Returns:
            Dictionary with graph summary
        """
        dataframe_nodes = [n for n in self.graph.nodes() if not n.startswith('op_')]
        operation_nodes = [n for n in self.graph.nodes() if n.startswith('op_')]
        
        return {
            'total_nodes': len(self.graph.nodes()),
            'total_edges': len(self.graph.edges()),
            'dataframe_nodes': len(dataframe_nodes),
            'operation_nodes': len(operation_nodes),
            'is_dag': nx.is_directed_acyclic_graph(self.graph),
            'has_cycles': not nx.is_directed_acyclic_graph(self.graph),
            'bottlenecks': self.find_bottlenecks()
        }
    
    def export_graph(self, format: str = 'json') -> str:
        """
        Export the lineage graph in various formats.
        
        Args:
            format: Export format ('json', 'dot', 'gml')
            
        Returns:
            String representation of the graph
        """
        if format == 'json':
            return json.dumps({
                'nodes': [asdict(node) for node in self.nodes.values()],
                'edges': [asdict(edge) for edge in self.edges]
            }, indent=2)
        elif format == 'dot':
            return nx.drawing.nx_pydot.to_pydot(self.graph).to_string()
        elif format == 'gml':
            return '\n'.join(nx.generate_gml(self.graph))
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def visualize_graph(self) -> str:
        """
        Generate an interactive HTML visualization of the lineage graph.
        
        Returns:
            HTML string for visualization
        """
        if not PYVIS_AVAILABLE:
            return "pyvis not available. Install with: pip install pyvis"
        
        try:
            # Create network
            net = network.Network(height='750px', width='100%', bgcolor='#ffffff', 
                                font_color='#000000', directed=True)
            
            # Add nodes
            for node_id, node_data in self.nodes.items():
                if node_data.node_type == 'dataframe':
                    net.add_node(node_id, label=node_id, color='#4CAF50', 
                               title=f"Dataframe: {node_id}")
                else:
                    net.add_node(node_id, label=node_data.metadata.get('operation_name', node_id), 
                               color='#2196F3', title=f"Operation: {node_id}")
            
            # Add edges
            for edge in self.edges:
                net.add_edge(edge.source_id, edge.target_id, 
                           title=edge.edge_type, arrows='to')
            
            # Generate HTML
            return net.generate_html()
        except Exception as e:
            return f"Error generating visualization: {str(e)}"
    
    def get_operation_chain(self, source_df: str, target_df: str) -> List[str]:
        """
        Get the chain of operations between two dataframes.
        
        Args:
            source_df: Source dataframe ID
            target_df: Target dataframe ID
            
        Returns:
            List of operation IDs in the chain
        """
        try:
            path = nx.shortest_path(self.graph, source_df, target_df)
            return [node for node in path if node.startswith('op_')]
        except nx.NetworkXNoPath:
            return [] 