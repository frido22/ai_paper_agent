#!/usr/bin/env python3
"""
Enhanced test script for argument graph extraction with improved prompts.

This script demonstrates the enhanced extraction capabilities including:
- Longer, more comprehensive component extraction
- New component types (Method, Result, Limitation)
- New relationship types (addresses, compares_to, builds_on, motivates, demonstrates)
- Better quality relationships with detailed explanations
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_approach.argument_extractor import extract_argument_graph
from src.graph_approach.config import Config
from src.ingestion.ingest import run_pipeline


def create_enhanced_test_pages() -> List[Dict[str, Any]]:
    """Create test page data that demonstrates the enhanced extraction capabilities."""
    return [
        {
            "page_number": 1,
            "text": """
            Introduction to Advanced Machine Learning Systems
            
            Machine learning has revolutionized numerous fields, from healthcare diagnostics to autonomous vehicle navigation. 
            However, existing systems often struggle with interpretability, robustness, and generalization across diverse domains. 
            This paper presents a novel approach that addresses these fundamental limitations through a multi-modal architecture 
            that combines deep learning with symbolic reasoning.
            
            Our primary contribution is a hybrid system that achieves state-of-the-art performance while maintaining 
            interpretability through explicit reasoning chains. We demonstrate that this approach not only improves 
            accuracy by 23% compared to baseline methods but also provides human-readable explanations for its decisions. 
            Furthermore, our system shows remarkable robustness when tested on out-of-distribution data, maintaining 
            89% performance compared to 67% for traditional approaches.
            
            The key innovation lies in our novel attention mechanism that dynamically selects relevant features 
            and constructs interpretable decision trees. This method consists of three main components: a feature 
            extraction module, a reasoning engine, and an explanation generator. The feature extraction module 
            processes raw input data and identifies salient patterns, while the reasoning engine applies symbolic 
            logic to construct decision paths. Finally, the explanation generator translates these paths into 
            natural language descriptions that humans can understand and verify.
            
            However, our approach does have some limitations. The symbolic reasoning component requires domain-specific 
            knowledge engineering, which can be time-consuming for new applications. Additionally, the system's 
            computational complexity scales with the number of reasoning rules, potentially limiting its applicability 
            to real-time systems. We address these limitations by proposing an automated knowledge extraction 
            pipeline and optimized inference algorithms that reduce computational overhead by 40%.
            """,
            "tables": [],
            "text_stats": {"word_count": 280, "char_count": 1850, "line_count": 25, "table_count": 0}
        },
        {
            "page_number": 2,
            "text": """
            Experimental Results and Comparative Analysis
            
            We evaluated our hybrid system across three challenging domains: medical diagnosis, financial fraud 
            detection, and autonomous driving decision-making. Our experiments involved datasets with over 100,000 
            samples each, representing real-world complexity and diversity. The medical diagnosis dataset contained 
            patient records from five major hospitals, while the financial dataset included transaction data from 
            a global banking network. The autonomous driving dataset comprised sensor readings from urban and 
            highway environments.
            
            Our results demonstrate consistent improvements across all domains. In medical diagnosis, our system 
            achieved 94.2% accuracy with 91% interpretability score, compared to 87.1% accuracy and 23% 
            interpretability for the best baseline method. The financial fraud detection experiments showed 
            similar improvements, with our approach achieving 96.8% precision and 94.1% recall, outperforming 
            traditional machine learning methods by 15% and 12% respectively. In autonomous driving, our system 
            maintained 89.3% decision accuracy in challenging scenarios where baseline methods dropped to 67.2%.
            
            The comparative analysis reveals several key insights. First, our hybrid approach consistently 
            outperforms purely neural methods in terms of both accuracy and interpretability. Second, the 
            symbolic reasoning component provides significant robustness benefits, especially in edge cases 
            and adversarial scenarios. Third, the explanation quality correlates strongly with user trust 
            and adoption rates in real-world deployments.
            
            Despite these promising results, we acknowledge several limitations of our current approach. 
            The system's performance degrades when dealing with highly ambiguous or contradictory data, 
            requiring additional preprocessing and validation steps. Furthermore, the symbolic reasoning 
            rules need to be carefully crafted to avoid bias and ensure fairness across different demographic 
            groups. We are actively working on addressing these challenges through improved data preprocessing 
            pipelines and fairness-aware rule generation.
            """,
            "tables": [],
            "text_stats": {"word_count": 320, "char_count": 2100, "line_count": 28, "table_count": 0}
        }
    ]


def test_enhanced_extraction():
    """Test the enhanced argument graph extraction."""
    print("🧪 Testing Enhanced Argument Graph Extraction")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not Config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Create enhanced test data
    print("📄 Creating enhanced test page data...")
    pages = create_enhanced_test_pages()
    print(f"   Created {len(pages)} test pages with comprehensive content")
    
    # Show configuration
    print(f"\n⚙️  Enhanced Configuration:")
    print(f"   Pages per chunk: {Config.PAGES_PER_CHUNK}")
    print(f"   OpenAI model: {Config.OPENAI_MODEL}")
    print(f"   Temperature: {Config.OPENAI_TEMPERATURE}")
    print(f"   New component types: Method, Result, Limitation")
    print(f"   New relationship types: addresses, compares_to, builds_on, motivates, demonstrates")
    
    # Extract argument graph
    print(f"\n🔍 Extracting enhanced argument graph...")
    try:
        result = extract_argument_graph(pages)
        
        # Display results
        print(f"\n✅ Enhanced extraction completed successfully!")
        print(f"📊 Results:")
        print(f"   Components found: {len(result['nodes'])}")
        print(f"   Relationships found: {len(result['edges'])}")
        
        # Show component breakdown by type
        component_types = {}
        for node in result['nodes']:
            comp_type = node['type']
            component_types[comp_type] = component_types.get(comp_type, 0) + 1
        
        print(f"\n📝 Component Breakdown:")
        for comp_type, count in component_types.items():
            print(f"   {comp_type}: {count}")
        
        # Show relationship breakdown by type
        relation_types = {}
        for edge in result['edges']:
            rel_type = edge['relation']
            relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
        
        print(f"\n🔗 Relationship Breakdown:")
        for rel_type, count in relation_types.items():
            print(f"   {rel_type}: {count}")
        
        # Show sample components with longer text
        if result['nodes']:
            print(f"\n📝 Sample Enhanced Components:")
            for i, node in enumerate(result['nodes'][:3]):
                print(f"   {i+1}. {node['type']} (ID: {node['id']}, Page: {node['page']})")
                print(f"      Text length: {len(node['text'])} characters")
                print(f"      Text: {node['text'][:150]}...")
                print()
        
        # Show sample relationships with explanations
        if result['edges']:
            print(f"\n🔗 Sample Enhanced Relationships:")
            for i, edge in enumerate(result['edges'][:3]):
                print(f"   {i+1}. {edge['source']} --[{edge['relation']}]--> {edge['target']}")
                print(f"      Page: {edge['page']}")
                if 'explanation' in edge:
                    print(f"      Explanation: {edge['explanation'][:100]}...")
                print()
        
        # Save results
        output_file = "enhanced_extraction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Enhanced results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during enhanced extraction: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🚀 Enhanced Argument Graph Extraction Test")
    print("=" * 60)
    print("Testing improved prompts with:")
    print("• Longer, more comprehensive component extraction")
    print("• New component types (Method, Result, Limitation)")
    print("• New relationship types (addresses, compares_to, builds_on, motivates, demonstrates)")
    print("• Better quality relationships with detailed explanations")
    print()
    
    success = test_enhanced_extraction()
    
    if success:
        print(f"\n🎉 Enhanced test completed successfully!")
        print(f"📁 Check 'enhanced_extraction_result.json' for detailed results")
        print(f"🔍 Compare with previous results to see improvements")
    else:
        print(f"\n💥 Enhanced test failed. Please check the error messages above.")


if __name__ == "__main__":
    main() 