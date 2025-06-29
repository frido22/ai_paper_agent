"""
Data structures for argument graph components.

This module defines the core data structures used to represent
argumentative components and their relationships in a graph format.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ArgumentComponent:
    """
    Represents an argumentative component in the text.
    
    Attributes:
        id: Unique identifier for the component
        type: Type of argumentative component (Claim, Evidence, Conclusion, etc.)
        text: The exact text span of the component
        page: Page number where the component was found
    """
    id: str
    type: str
    text: str
    page: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return asdict(self)


@dataclass
class ArgumentRelation:
    """
    Represents a logical relationship between two argumentative components.
    
    Attributes:
        source: ID of the source component
        target: ID of the target component
        relation: Type of relationship (supported_by, contradicted_by, etc.)
        page: Page number where the relationship is established
    """
    source: str
    target: str
    relation: str
    page: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        return asdict(self)


class ArgumentGraph:
    """
    Container for argumentative components and their relationships.
    
    This class manages a collection of nodes (components) and edges (relationships)
    and provides methods to add elements and export the graph structure.
    """
    
    def __init__(self):
        """Initialize an empty argument graph."""
        self.nodes: List[ArgumentComponent] = []
        self.edges: List[ArgumentRelation] = []
    
    def add_node(self, component: ArgumentComponent) -> None:
        """
        Add a component to the graph.
        
        Args:
            component: The argumentative component to add
        """
        # Check if component with same ID already exists
        if not any(node.id == component.id for node in self.nodes):
            self.nodes.append(component)
    
    def add_edge(self, relation: ArgumentRelation) -> None:
        """
        Add a relationship to the graph.
        
        Args:
            relation: The argumentative relationship to add
        """
        # Check if both source and target nodes exist
        source_exists = any(node.id == relation.source for node in self.nodes)
        target_exists = any(node.id == relation.target for node in self.nodes)
        
        if source_exists and target_exists:
            # Check if this relationship already exists
            if not any(edge.source == relation.source and 
                      edge.target == relation.target and 
                      edge.relation == relation.relation for edge in self.edges):
                self.edges.append(relation)
    
    def get_node_by_id(self, node_id: str) -> Optional[ArgumentComponent]:
        """
        Get a component by its ID.
        
        Args:
            node_id: The ID of the component to find
            
        Returns:
            The component if found, None otherwise
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_nodes_by_type(self, component_type: str) -> List[ArgumentComponent]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The type of components to retrieve
            
        Returns:
            List of components of the specified type
        """
        return [node for node in self.nodes if node.type == component_type]
    
    def get_nodes_by_page(self, page_number: int) -> List[ArgumentComponent]:
        """
        Get all components from a specific page.
        
        Args:
            page_number: The page number to filter by
            
        Returns:
            List of components from the specified page
        """
        return [node for node in self.nodes if node.page == page_number]
    
    def get_edges_by_page(self, page_number: int) -> List[ArgumentRelation]:
        """
        Get all relationships from a specific page.
        
        Args:
            page_number: The page number to filter by
            
        Returns:
            List of relationships from the specified page
        """
        return [edge for edge in self.edges if edge.page == page_number]
    
    def get_edges_by_relation_type(self, relation_type: str) -> List[ArgumentRelation]:
        """
        Get all relationships of a specific type.
        
        Args:
            relation_type: The type of relationships to retrieve
            
        Returns:
            List of relationships of the specified type
        """
        return [edge for edge in self.edges if edge.relation == relation_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the graph to a dictionary format for JSON serialization.
        
        Returns:
            Dictionary containing nodes and edges lists
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the graph structure.
        
        Returns:
            Dictionary containing various statistics about the graph
        """
        stats = {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": {},
            "edges_by_relation": {},
            "nodes_by_page": {},
            "edges_by_page": {}
        }
        
        # Count nodes by type
        for node in self.nodes:
            stats["nodes_by_type"][node.type] = stats["nodes_by_type"].get(node.type, 0) + 1
        
        # Count edges by relation type
        for edge in self.edges:
            stats["edges_by_relation"][edge.relation] = stats["edges_by_relation"].get(edge.relation, 0) + 1
        
        # Count nodes by page
        for node in self.nodes:
            stats["nodes_by_page"][node.page] = stats["nodes_by_page"].get(node.page, 0) + 1
        
        # Count edges by page
        for edge in self.edges:
            stats["edges_by_page"][edge.page] = stats["edges_by_page"].get(edge.page, 0) + 1
        
        return stats
    
    def validate(self) -> List[str]:
        """
        Validate the graph structure and return any issues found.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check for orphaned edges (edges pointing to non-existent nodes)
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge source '{edge.source}' does not exist")
            if edge.target not in node_ids:
                errors.append(f"Edge target '{edge.target}' does not exist")
        
        # Check for duplicate node IDs
        seen_ids = set()
        for node in self.nodes:
            if node.id in seen_ids:
                errors.append(f"Duplicate node ID: {node.id}")
            seen_ids.add(node.id)
        
        # Check for self-loops (edges from a node to itself)
        for edge in self.edges:
            if edge.source == edge.target:
                errors.append(f"Self-loop detected: {edge.source} -> {edge.target}")
        
        return errors 