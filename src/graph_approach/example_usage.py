"""
Example usage of the argument graph extraction system.

This script demonstrates how to use the extract_argument_graph function
with sample data and shows how to process the results.
"""

import json
import os
from typing import List, Dict, Any
from .argument_extractor import extract_argument_graph
from .config import Config


def create_sample_pages() -> List[Dict[str, Any]]:
    """
    Create sample page data for testing.
    
    Returns:
        List of sample page dictionaries
    """
    return [
        {
            "page_number": 1,
            "text": """
            Introduction
            
            Machine learning has revolutionized many fields in recent years. 
            Deep learning models, in particular, have shown remarkable performance 
            in image recognition tasks. However, these models often require 
            large amounts of labeled data for training.
            
            This paper argues that transfer learning can significantly reduce 
            the data requirements for training deep learning models. We present 
            evidence from multiple experiments showing that pre-trained models 
            can achieve comparable performance with only 10% of the original 
            training data.
            
            Our main claim is that transfer learning is more effective than 
            training from scratch when limited data is available. This conclusion 
            is supported by our experimental results across three different datasets.
            """,
            "tables": [],
            "text_stats": {"word_count": 150, "char_count": 800, "line_count": 15, "table_count": 0}
        },
        {
            "page_number": 2,
            "text": """
            Methodology and Results
            
            We conducted experiments on three benchmark datasets: CIFAR-10, 
            ImageNet, and MNIST. For each dataset, we compared the performance 
            of models trained from scratch versus models using transfer learning.
            
            The results clearly demonstrate the superiority of transfer learning. 
            Models using pre-trained weights achieved 85% accuracy on CIFAR-10 
            with only 5,000 training samples, while models trained from scratch 
            achieved only 65% accuracy with the same amount of data.
            
            However, some researchers argue that transfer learning may not work 
            well for domain-specific tasks. Our experiments on medical imaging 
            data show that this concern is largely unfounded. Transfer learning 
            models still outperform scratch-trained models by 15% on average.
            
            These findings lead us to conclude that transfer learning should be 
            the default approach when training deep learning models with limited data.
            """,
            "tables": [],
            "text_stats": {"word_count": 180, "char_count": 950, "line_count": 18, "table_count": 0}
        },
        {
            "page_number": 3,
            "text": """
            Discussion and Future Work
            
            The implications of our findings extend beyond the specific datasets 
            we tested. Transfer learning appears to be a general principle that 
            applies across different domains and model architectures.
            
            One limitation of our study is that we focused primarily on computer 
            vision tasks. Future work should investigate whether similar benefits 
            exist in natural language processing and other domains.
            
            Additionally, we need to better understand the mechanisms behind 
            transfer learning's effectiveness. This understanding could lead to 
            even more efficient transfer learning techniques.
            
            In conclusion, our research demonstrates that transfer learning 
            significantly reduces data requirements while maintaining or improving 
            model performance across multiple domains.
            """,
            "tables": [],
            "text_stats": {"word_count": 160, "char_count": 850, "line_count": 16, "table_count": 0}
        }
    ]


def analyze_graph_results(graph_data: Dict[str, Any]) -> None:
    """
    Analyze and display the results of argument graph extraction.
    
    Args:
        graph_data: The graph data returned by extract_argument_graph
    """
    print("=== Argument Graph Analysis Results ===\n")
    
    # Display nodes
    print(f"Total Components Found: {len(graph_data['nodes'])}")
    print("\nComponents by Type:")
    type_counts = {}
    for node in graph_data['nodes']:
        node_type = node['type']
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
    
    for node_type, count in type_counts.items():
        print(f"  {node_type}: {count}")
    
    print(f"\nComponents by Page:")
    page_counts = {}
    for node in graph_data['nodes']:
        page = node['page']
        page_counts[page] = page_counts.get(page, 0) + 1
    
    for page, count in sorted(page_counts.items()):
        print(f"  Page {page}: {count}")
    
    # Display edges
    print(f"\nTotal Relationships Found: {len(graph_data['edges'])}")
    print("\nRelationships by Type:")
    relation_counts = {}
    for edge in graph_data['edges']:
        relation_type = edge['relation']
        relation_counts[relation_type] = relation_counts.get(relation_type, 0) + 1
    
    for relation_type, count in relation_counts.items():
        print(f"  {relation_type}: {count}")
    
    # Display sample components
    print("\n=== Sample Components ===")
    for i, node in enumerate(graph_data['nodes'][:5]):  # Show first 5 components
        print(f"\n{i+1}. {node['type']} (ID: {node['id']}, Page: {node['page']})")
        print(f"   Text: {node['text'][:100]}...")
    
    # Display sample relationships
    print("\n=== Sample Relationships ===")
    for i, edge in enumerate(graph_data['edges'][:5]):  # Show first 5 relationships
        print(f"\n{i+1}. {edge['source']} --[{edge['relation']}]--> {edge['target']} (Page: {edge['page']})")


def save_graph_to_json(graph_data: Dict[str, Any], filename: str = "argument_graph.json") -> None:
    """
    Save the graph data to a JSON file.
    
    Args:
        graph_data: The graph data to save
        filename: Name of the output file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    print(f"\nGraph data saved to {filename}")


def demonstrate_chunk_processing() -> None:
    """
    Demonstrate the chunk-based processing approach.
    """
    print("=== Chunk-Based Processing Demonstration ===\n")
    
    # Show configuration
    chunk_config = Config.get_chunk_config()
    print("Chunk Processing Configuration:")
    for key, value in chunk_config.items():
        print(f"  {key}: {value}")
    
    print(f"\nWith {Config.PAGES_PER_CHUNK} pages per chunk, a 10-page paper would be processed in:")
    pages = 10
    chunks = (pages + Config.PAGES_PER_CHUNK - 1) // Config.PAGES_PER_CHUNK
    print(f"  {chunks} chunks instead of {pages} individual API calls")
    print(f"  This represents a {(1 - chunks/pages) * 100:.1f}% reduction in API calls!")


def main():
    """
    Main function demonstrating the usage of argument graph extraction.
    """
    print("Argument Graph Extraction Example")
    print("=================================\n")
    
    # Check if OpenAI API key is set
    if not Config.OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key before running this example.")
        print("You can set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Demonstrate chunk processing
    demonstrate_chunk_processing()
    
    # Create sample pages
    print("\nCreating sample page data...")
    pages = create_sample_pages()
    
    # Extract argument graph
    print("Extracting argument graph...")
    try:
        graph_data = extract_argument_graph(pages)
        
        # Analyze results
        analyze_graph_results(graph_data)
        
        # Save to file
        save_graph_to_json(graph_data)
        
        print("\n=== Example completed successfully! ===")
        print("\nKey improvements with chunk-based processing:")
        print("✅ Reduced API calls through batch processing")
        print("✅ Better context awareness with previous components")
        print("✅ More accurate cross-page relationships")
        print("✅ Improved efficiency for large papers")
        
    except Exception as e:
        print(f"Error during argument graph extraction: {e}")
        print("Please check your OpenAI API key and internet connection.")


if __name__ == "__main__":
    main() 