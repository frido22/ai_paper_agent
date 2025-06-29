#!/usr/bin/env python3
"""
Simple test script for argument graph extraction.

This script can be run directly to test the extraction functionality.
"""

import os
import sys
import json
from typing import List, Dict, Any

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_approach.argument_extractor import extract_argument_graph
from src.graph_approach.config import Config
from src.ingestion.ingest import run_pipeline


def create_test_pages() -> List[Dict[str, Any]]:
    """Create test page data."""
    print("🧪 Testing Argument Graph Extraction")
    print("=" * 50)
    res = run_pipeline()
    print(res)
    return res[0].pages


def test_extraction():
    """Test the argument graph extraction."""
    print("🧪 Testing Argument Graph Extraction")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not Config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Create test data
    print("📄 Creating test page data...")
    pages = create_test_pages()
    print(f"   Created {len(pages)} test pages")
    
    # Show configuration
    print(f"\n⚙️  Configuration:")
    print(f"   Pages per chunk: {Config.PAGES_PER_CHUNK}")
    print(f"   OpenAI model: {Config.OPENAI_MODEL}")
    print(f"   Temperature: {Config.OPENAI_TEMPERATURE}")
    
    # Extract argument graph
    print(f"\n🔍 Extracting argument graph...")
    try:
        result = extract_argument_graph(pages)
        
        # Display results
        print(f"\n✅ Extraction completed successfully!")
        print(f"📊 Results:")
        print(f"   Components found: {len(result['nodes'])}")
        print(f"   Relationships found: {len(result['edges'])}")
        
        # Show sample components
        if result['nodes']:
            print(f"\n📝 Sample Components:")
            for i, node in enumerate(result['nodes'][:3]):
                print(f"   {i+1}. {node['type']} (ID: {node['id']}, Page: {node['page']})")
                print(f"      Text: {node['text'][:80]}...")
        
        # Show sample relationships
        if result['edges']:
            print(f"\n🔗 Sample Relationships:")
            for i, edge in enumerate(result['edges'][:3]):
                print(f"   {i+1}. {edge['source']} --[{edge['relation']}]--> {edge['target']}")
        
        # Save results
        output_file = "test_extraction_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🚀 Argument Graph Extraction Test")
    print("=" * 50)
    
    success = test_extraction()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Check 'test_extraction_result.json' for detailed results")
    else:
        print(f"\n💥 Test failed. Please check the error messages above.")


if __name__ == "__main__":
    main() 