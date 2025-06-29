"""
Advanced graph analysis utilities for dynamic knowledge graph processing.

This module provides utilities for analyzing argument graphs and providing
recommendations for visualization and further processing based on graph characteristics.
"""

from typing import Dict, Any, List, Tuple, Optional
import math
from .components import ArgumentGraph, ArgumentComponent, ArgumentRelation


class GraphAnalyzer:
    """
    Advanced analyzer for argument graphs that provides insights and recommendations.
    """
    
    def __init__(self, graph: ArgumentGraph):
        """
        Initialize the analyzer with a graph.
        
        Args:
            graph: The ArgumentGraph to analyze
        """
        self.graph = graph
        self.stats = graph.get_statistics()
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """
        Analyze the complexity of the argument graph.
        
        Returns:
            Dictionary containing complexity metrics and recommendations
        """
        total_nodes = self.stats["total_nodes"]
        total_edges = self.stats["total_edges"]
        
        # Calculate complexity metrics
        if total_nodes == 0:
            return {"complexity": "empty", "recommendations": ["Add content to analyze"]}
        
        density = total_edges / max(1, (total_nodes * (total_nodes - 1) / 2))
        avg_connections = total_edges / total_nodes
        type_diversity = len(self.stats["nodes_by_type"])
        
        # Determine complexity level
        complexity_score = (
            min(total_nodes / 50, 1.0) * 0.4 +  # Size factor
            min(density * 10, 1.0) * 0.3 +      # Density factor
            min(avg_connections / 5, 1.0) * 0.2 + # Connection factor
            min(type_diversity / 8, 1.0) * 0.1   # Diversity factor
        )
        
        if complexity_score < 0.3:
            complexity_level = "simple"
        elif complexity_score < 0.6:
            complexity_level = "moderate"
        elif complexity_score < 0.8:
            complexity_level = "complex"
        else:
            complexity_level = "highly_complex"
        
        return {
            "complexity_level": complexity_level,
            "complexity_score": complexity_score,
            "metrics": {
                "node_count": total_nodes,
                "edge_count": total_edges,
                "density": density,
                "average_connections": avg_connections,
                "type_diversity": type_diversity
            },
            "recommendations": self._get_complexity_recommendations(complexity_level, total_nodes, total_edges)
        }
    
    def suggest_visualization_config(self) -> Dict[str, Any]:
        """
        Suggest optimal visualization configuration based on graph characteristics.
        
        Returns:
            Dictionary containing visualization recommendations
        """
        complexity = self.analyze_complexity()
        total_nodes = self.stats["total_nodes"]
        total_edges = self.stats["total_edges"]
        
        # Base configuration
        config = {
            "layout": "force-directed",
            "node_sizing": "degree-based",
            "edge_bundling": False,
            "clustering": False,
            "filtering": False,
            "interactive_features": ["zoom", "pan", "node_hover"],
            "performance_optimizations": []
        }
        
        # Adjust based on size
        if total_nodes > 100:
            config["layout"] = "hierarchical"
            config["clustering"] = True
            config["performance_optimizations"].append("level_of_detail")
            config["interactive_features"].append("progressive_loading")
        
        if total_nodes > 50:
            config["edge_bundling"] = True
            config["filtering"] = True
            config["interactive_features"].append("component_filtering")
        
        # Adjust based on density
        if total_edges / max(1, total_nodes) > 3:
            config["edge_bundling"] = True
            config["interactive_features"].append("edge_filtering")
        
        # Add component-specific recommendations
        component_types = list(self.stats["nodes_by_type"].keys())
        config["color_scheme"] = self._suggest_color_scheme(component_types)
        config["node_shapes"] = self._suggest_node_shapes(component_types)
        
        return config
    
    def get_key_insights(self) -> List[Dict[str, Any]]:
        """
        Extract key insights from the argument graph.
        
        Returns:
            List of insights with descriptions and supporting data
        """
        insights = []
        
        # Insight about argument structure
        claim_count = self.stats["nodes_by_type"].get("Claim", 0)
        evidence_count = self.stats["nodes_by_type"].get("Evidence", 0)
        
        if claim_count > 0 and evidence_count > 0:
            evidence_to_claim_ratio = evidence_count / claim_count
            insights.append({
                "type": "argumentation_balance",
                "title": "Evidence to Claims Ratio",
                "description": f"The document has {evidence_to_claim_ratio:.1f} evidence components per claim",
                "interpretation": self._interpret_evidence_ratio(evidence_to_claim_ratio),
                "data": {"claims": claim_count, "evidence": evidence_count, "ratio": evidence_to_claim_ratio}
            })
        
        # Insight about document structure
        pages_with_content = len([p for p, count in self.stats["nodes_by_page"].items() if count > 0])
        total_pages = max(self.stats["nodes_by_page"].keys()) if self.stats["nodes_by_page"] else 0
        
        if total_pages > 0:
            content_density = pages_with_content / total_pages
            insights.append({
                "type": "content_distribution",
                "title": "Content Distribution",
                "description": f"{content_density:.1%} of pages contain argumentative content",
                "interpretation": self._interpret_content_density(content_density),
                "data": {"content_pages": pages_with_content, "total_pages": total_pages, "density": content_density}
            })
        
        # Insight about connectivity
        most_connected = self.stats["graph_metrics"].get("most_connected_components", [])
        if most_connected:
            top_component = most_connected[0]
            insights.append({
                "type": "central_components",
                "title": "Most Connected Component",
                "description": f"'{top_component['type']}' component with {top_component['connection_count']} connections",
                "interpretation": "This component plays a central role in the argument structure",
                "data": top_component
            })
        
        # Insight about relationship patterns
        relation_types = self.stats["edges_by_relation"]
        if relation_types:
            dominant_relation = max(relation_types.items(), key=lambda x: x[1])
            insights.append({
                "type": "relationship_patterns",
                "title": "Dominant Relationship Type",
                "description": f"'{dominant_relation[0]}' relationships are most common ({dominant_relation[1]} instances)",
                "interpretation": self._interpret_dominant_relation(dominant_relation[0]),
                "data": {"relation_type": dominant_relation[0], "count": dominant_relation[1], "all_relations": relation_types}
            })
        
        return insights
    
    def suggest_improvements(self) -> List[Dict[str, str]]:
        """
        Suggest improvements to the argument graph extraction or structure.
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        complexity = self.analyze_complexity()
        
        # Suggestions based on complexity
        if complexity["complexity_level"] == "simple":
            suggestions.append({
                "category": "extraction",
                "suggestion": "Consider extracting more detailed components",
                "reason": "The graph appears simple and might benefit from more granular analysis"
            })
        
        # Suggestions based on balance
        component_types = self.stats["nodes_by_type"]
        if "Claim" in component_types and "Evidence" in component_types:
            ratio = component_types["Evidence"] / component_types["Claim"]
            if ratio < 0.5:
                suggestions.append({
                    "category": "balance",
                    "suggestion": "Look for additional supporting evidence",
                    "reason": f"Low evidence-to-claim ratio ({ratio:.1f}) suggests claims may be under-supported"
                })
        
        # Suggestions based on connectivity
        avg_connections = self.stats["graph_metrics"].get("average_connections_per_node", 0)
        if avg_connections < 1:
            suggestions.append({
                "category": "connectivity",
                "suggestion": "Improve relationship detection",
                "reason": "Low connectivity suggests missing logical relationships between components"
            })
        
        # Suggestions based on type diversity
        if len(component_types) < 4:
            suggestions.append({
                "category": "diversity",
                "suggestion": "Expand component type coverage",
                "reason": "Limited component types may indicate incomplete argumentative analysis"
            })
        
        return suggestions
    
    def _get_complexity_recommendations(self, complexity_level: str, nodes: int, edges: int) -> List[str]:
        """Get recommendations based on complexity level."""
        recommendations = []
        
        if complexity_level == "simple":
            recommendations.extend([
                "Consider using a simple force-directed layout",
                "Basic node-link visualization should work well",
                "Focus on clear labeling and component types"
            ])
        elif complexity_level == "moderate":
            recommendations.extend([
                "Use hierarchical or clustered layouts",
                "Consider grouping related components",
                "Add interactive filtering options"
            ])
        elif complexity_level in ["complex", "highly_complex"]:
            recommendations.extend([
                "Use advanced layout algorithms (e.g., multi-level force-directed)",
                "Implement progressive disclosure techniques",
                "Consider matrix or parallel coordinate visualizations",
                "Add strong filtering and search capabilities",
                "Use edge bundling to reduce visual clutter"
            ])
        
        if nodes > 50:
            recommendations.append("Consider implementing level-of-detail rendering")
        
        if edges > 100:
            recommendations.append("Use edge bundling or aggregation techniques")
        
        return recommendations
    
    def _suggest_color_scheme(self, component_types: List[str]) -> Dict[str, str]:
        """Suggest colors for different component types."""
        color_schemes = {
            "Claim": "#2E86AB",      # Blue - primary assertions
            "Evidence": "#A23B72",    # Purple - supporting data
            "Conclusion": "#F18F01",  # Orange - final outcomes
            "Background": "#C73E1D",  # Red - contextual info
            "Method": "#86C232",      # Green - methodological
            "Result": "#FFB84D",      # Light orange - findings
            "Limitation": "#6C757D",  # Gray - constraints
            "Counterclaim": "#DC3545" # Dark red - opposing views
        }
        
        return {comp_type: color_schemes.get(comp_type, "#6C757D") for comp_type in component_types}
    
    def _suggest_node_shapes(self, component_types: List[str]) -> Dict[str, str]:
        """Suggest shapes for different component types."""
        shape_schemes = {
            "Claim": "circle",
            "Evidence": "square",
            "Conclusion": "diamond",
            "Background": "triangle",
            "Method": "hexagon",
            "Result": "star",
            "Limitation": "cross",
            "Counterclaim": "triangle-down"
        }
        
        return {comp_type: shape_schemes.get(comp_type, "circle") for comp_type in component_types}
    
    def _interpret_evidence_ratio(self, ratio: float) -> str:
        """Interpret the evidence to claims ratio."""
        if ratio < 0.5:
            return "Claims may be under-supported with limited evidence"
        elif ratio < 1.5:
            return "Balanced relationship between claims and supporting evidence"
        elif ratio < 3.0:
            return "Well-supported arguments with substantial evidence"
        else:
            return "Highly evidence-dense document with comprehensive support"
    
    def _interpret_content_density(self, density: float) -> str:
        """Interpret content density across pages."""
        if density < 0.3:
            return "Sparse argumentative content - consider more comprehensive extraction"
        elif density < 0.7:
            return "Moderate argumentative density - typical for academic papers"
        else:
            return "High argumentative density - comprehensive argumentative structure"
    
    def _interpret_dominant_relation(self, relation_type: str) -> str:
        """Interpret the dominant relationship type."""
        interpretations = {
            "supported_by": "Evidence-focused argumentation with strong empirical support",
            "leads_to": "Sequential logical reasoning with clear progression",
            "elaborates": "Detailed explanatory structure with thorough development",
            "contradicted_by": "Critical analysis with attention to counterarguments",
            "builds_on": "Incremental knowledge building on existing work",
            "demonstrates": "Example-driven argumentation with concrete illustrations"
        }
        
        return interpretations.get(relation_type, "Structured logical relationships between components")


def analyze_graph_for_api(graph_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze a graph result from the API.
    
    Args:
        graph_result: Result dictionary from extract_argument_graph
        
    Returns:
        Dictionary containing analysis results
    """
    # Reconstruct graph from result
    from .components import ArgumentGraph, ArgumentComponent, ArgumentRelation
    
    graph = ArgumentGraph()
    
    # Add nodes
    for node_data in graph_result.get("nodes", []):
        component = ArgumentComponent(
            id=node_data["id"],
            type=node_data["type"],
            text=node_data["text"],
            page=node_data["page"]
        )
        graph.add_node(component)
    
    # Add edges
    for edge_data in graph_result.get("edges", []):
        relation = ArgumentRelation(
            source=edge_data["source"],
            target=edge_data["target"],
            relation=edge_data["relation"],
            page=edge_data["page"]
        )
        graph.add_edge(relation)
    
    # Analyze the graph
    analyzer = GraphAnalyzer(graph)
    
    return {
        "complexity_analysis": analyzer.analyze_complexity(),
        "visualization_config": analyzer.suggest_visualization_config(),
        "key_insights": analyzer.get_key_insights(),
        "improvement_suggestions": analyzer.suggest_improvements()
    }
