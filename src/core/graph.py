from typing import Dict, List, Set, Optional, Tuple
from uuid import UUID, uuid4
import toposort
from src.core.models import WorkflowModel, NodeInstanceModel, ConnectionModel

class GraphManager:
    def __init__(self):
        self.nodes: Dict[UUID, NodeInstanceModel] = {}
        self.connections: List[ConnectionModel] = []

    def add_node(self, node: NodeInstanceModel):
        self.nodes[node.instance_id] = node

    def remove_node(self, node_id: UUID):
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove associated connections
            self.connections = [c for c in self.connections if c.from_node != node_id and c.to_node != node_id]

    def add_connection(self, connection: ConnectionModel) -> bool:
        """
        Adds a connection and checks for cycles. Returns False if a cycle is created.
        """
        self.connections.append(connection)
        if not self.is_dag():
            self.connections.pop()
            return False
        return True

    def remove_connection(self, connection_id: UUID):
        self.connections = [c for c in self.connections if c.id != connection_id]

    def is_dag(self) -> bool:
        """
        Checks if the current graph is a Directed Acyclic Graph (DAG).
        """
        try:
            self.get_topological_sort()
            return True
        except toposort.CircularDependencyError:
            return False

    def get_topological_sort(self, ignore_ports: List[str] = None) -> List[Set[UUID]]:
        """
        Returns the nodes in topological order for execution.
        :param ignore_ports: List of port names to ignore when calculating dependencies (breaks cycles).
        """
        if ignore_ports is None:
            ignore_ports = ["break_condition"] # Default special ports that allow feedback
            
        data = {}
        # Ensure all nodes are in the data dictionary
        for node_id in self.nodes:
            data[node_id] = set()

        # Add dependencies from connections
        for conn in self.connections:
            # If the destination port is in the ignore list, don't count it as a hard dependency
            if conn.to_port in ignore_ports:
                continue
                
            data[conn.to_node].add(conn.from_node)
        
        try:
            return list(toposort.toposort(data))
        except toposort.CircularDependencyError as e:
            # Re-raise with more context
            raise toposort.CircularDependencyError(f"Workflow contains a cycle that couldn't be resolved: {e}")

    def to_model(self) -> WorkflowModel:
        return WorkflowModel(
            nodes=list(self.nodes.values()),
            connections=self.connections
        )

    def from_model(self, model: WorkflowModel):
        self.nodes = {node.instance_id: node for node in model.nodes}
        self.connections = model.connections
