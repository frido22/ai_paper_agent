"""
Integration example for argument graph extraction.

This script demonstrates how to integrate the argument graph extraction
system with real paper data and shows various ways to use the results.
"""

import json
import os
import sys
from typing import List, Dict, Any
from pathlib import Path

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.graph_approach.argument_extractor import extract_argument_graph
from src.graph_approach.config import Config
from src.graph_approach.components import ArgumentGraph


def load_paper_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load paper data from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing paper data
        
    Returns:
        List of page dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure the data has the expected structure
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'pages' in data:
            return data['pages']
        else:
            raise ValueError("Invalid data format. Expected list of pages or dict with 'pages' key.")
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return []
    except Exception as e:
        print(f"Error loading data: {e}")
        return []


def analyze_argument_structure(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform detailed analysis of the argument structure.
    
    Args:
        graph_data: The graph data returned by extract_argument_graph
        
    Returns:
        Dictionary containing analysis results
    """
    analysis = {
        "total_components": len(graph_data['nodes']),
        "total_relationships": len(graph_data['edges']),
        "components_by_type": {},
        "components_by_page": {},
        "relationships_by_type": {},
        "relationships_by_page": {},
        "argument_chains": [],
        "isolated_components": [],
        "most_connected_components": []
    }
    
    # Count components by type
    for node in graph_data['nodes']:
        node_type = node['type']
        analysis["components_by_type"][node_type] = analysis["components_by_type"].get(node_type, 0) + 1
        
        page = node['page']
        analysis["components_by_page"][page] = analysis["components_by_page"].get(page, 0) + 1
    
    # Count relationships by type
    for edge in graph_data['edges']:
        relation_type = edge['relation']
        analysis["relationships_by_type"][relation_type] = analysis["relationships_by_type"].get(relation_type, 0) + 1
        
        page = edge['page']
        analysis["relationships_by_page"][page] = analysis["relationships_by_page"].get(page, 0) + 1
    
    # Find isolated components (no relationships)
    connected_components = set()
    for edge in graph_data['edges']:
        connected_components.add(edge['source'])
        connected_components.add(edge['target'])
    
    for node in graph_data['nodes']:
        if node['id'] not in connected_components:
            analysis["isolated_components"].append({
                "id": node['id'],
                "type": node['type'],
                "text": node['text'][:100] + "..." if len(node['text']) > 100 else node['text']
            })
    
    # Find most connected components
    component_connections = {}
    for edge in graph_data['edges']:
        component_connections[edge['source']] = component_connections.get(edge['source'], 0) + 1
        component_connections[edge['target']] = component_connections.get(edge['target'], 0) + 1
    
    sorted_components = sorted(component_connections.items(), key=lambda x: x[1], reverse=True)
    for component_id, connection_count in sorted_components[:5]:
        component = next((node for node in graph_data['nodes'] if node['id'] == component_id), None)
        if component:
            analysis["most_connected_components"].append({
                "id": component_id,
                "type": component['type'],
                "connections": connection_count,
                "text": component['text'][:100] + "..." if len(component['text']) > 100 else component['text']
            })
    
    return analysis


def export_for_visualization(graph_data: Dict[str, Any], output_file: str) -> None:
    """
    Export graph data in a format suitable for visualization tools.
    
    Args:
        graph_data: The graph data to export
        output_file: Path to the output file
    """
    # Format for tools like Gephi, NetworkX, or D3.js
    visualization_data = {
        "nodes": [],
        "edges": []
    }
    
    # Convert nodes to visualization format
    for node in graph_data['nodes']:
        viz_node = {
            "id": node['id'],
            "label": node['text'][:50] + "..." if len(node['text']) > 50 else node['text'],
            "type": node['type'],
            "page": node['page'],
            "full_text": node['text']
        }
        visualization_data["nodes"].append(viz_node)
    
    # Convert edges to visualization format
    for edge in graph_data['edges']:
        viz_edge = {
            "source": edge['source'],
            "target": edge['target'],
            "relation": edge['relation'],
            "page": edge['page']
        }
        visualization_data["edges"].append(viz_edge)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(visualization_data, f, indent=2, ensure_ascii=False)
    
    print(f"Visualization data exported to: {output_file}")


def generate_argument_summary(graph_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of the argument structure.
    
    Args:
        graph_data: The graph data to summarize
        
    Returns:
        String containing the summary
    """
    analysis = analyze_argument_structure(graph_data)
    
    summary = f"""
Argument Structure Summary
==========================

Total Components: {analysis['total_components']}
Total Relationships: {analysis['total_relationships']}

Component Distribution:
"""
    
    for component_type, count in analysis['components_by_type'].items():
        summary += f"  {component_type}: {count}\n"
    
    summary += f"\nRelationship Distribution:\n"
    for relation_type, count in analysis['relationships_by_type'].items():
        summary += f"  {relation_type}: {count}\n"
    
    if analysis['isolated_components']:
        summary += f"\nIsolated Components ({len(analysis['isolated_components'])}):\n"
        for comp in analysis['isolated_components'][:3]:  # Show first 3
            summary += f"  - {comp['type']}: {comp['text']}\n"
    
    if analysis['most_connected_components']:
        summary += f"\nMost Connected Components:\n"
        for comp in analysis['most_connected_components']:
            summary += f"  - {comp['type']} ({comp['connections']} connections): {comp['text']}\n"
    
    return summary


def main():
    """
    Main function demonstrating integration with real data.
    """
    print("Argument Graph Extraction - Integration Example")
    print("==============================================\n")
    
    # Check for OpenAI API key
    if not Config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key before running this example.")
        return
    
    # Example 1: Load data from file (if available)
    data_file = "paper_data.json"
    if os.path.exists(data_file):
        print(f"Loading paper data from {data_file}...")
        pages = load_paper_data(data_file)
        if not pages:
            print("No valid data found in file. Using sample data instead.")
            pages = create_sample_pages()
    else:
        print("No data file found. Using sample data...")
        pages = create_sample_pages()
    
    print(f"Processing {len(pages)} pages...")
    
    # Extract argument graph
    try:
        print("Extracting argument graph...")
        graph_data = extract_argument_graph(pages)
        
        # Analyze results
        print("\n" + "="*50)
        print("ANALYSIS RESULTS")
        print("="*50)
        
        summary = generate_argument_summary(graph_data)
        print(summary)
        
        # Export for visualization
        print("\n" + "="*50)
        print("EXPORTING DATA")
        print("="*50)
        
        export_for_visualization(graph_data, "argument_graph_viz.json")
        
        # Save raw data
        with open("argument_graph_raw.json", 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print("Raw graph data saved to: argument_graph_raw.json")
        
        print("\n" + "="*50)
        print("INTEGRATION COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"Error during argument graph extraction: {e}")
        import traceback
        traceback.print_exc()


def create_sample_pages() -> List[Dict[str, Any]]:
    """
    Create sample page data for demonstration.
    
    Returns:
        List of sample page dictionaries
    """
    return [
        {
            "page_number": 1,
            "text": """
            Introduction to Machine Learning Applications
            
            Machine learning has become a cornerstone of modern technology, 
            revolutionizing fields from healthcare to finance. This paper 
            presents a comprehensive analysis of machine learning applications 
            in real-world scenarios.
            
            Our primary claim is that machine learning significantly improves 
            decision-making processes across various domains. We support this 
            claim with extensive experimental evidence and case studies.
            
            However, some critics argue that machine learning systems lack 
            interpretability, making them unsuitable for critical applications. 
            We address this concern by presenting new interpretability techniques.
            """,
            "tables": [],
            "text_stats": {"word_count": 120, "char_count": 650, "line_count": 12, "table_count": 0}
        },
        {
            "page_number": 2,
            "text": """
            Experimental Results and Analysis
            
            We conducted experiments across three major domains: medical 
            diagnosis, financial forecasting, and autonomous systems. Our 
            results demonstrate consistent improvements in accuracy and 
            efficiency when using machine learning approaches.
            
            In medical diagnosis, our machine learning system achieved 94% 
            accuracy compared to 87% for traditional rule-based systems. 
            This improvement directly supports our claim about the effectiveness 
            of machine learning in critical applications.
            
            The financial forecasting experiments showed similar improvements, 
            with machine learning models outperforming traditional statistical 
            methods by 12% on average. These results further validate our 
            conclusions about the broad applicability of machine learning.
            """,
            "tables": [],
            "text_stats": {"word_count": 140, "char_count": 720, "line_count": 14, "table_count": 0}
        }
    ]


if __name__ == "__main__":
    main() 