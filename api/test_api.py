#!/usr/bin/env python3
"""
Test script for the Argument Graph Extraction API.

This script demonstrates how to upload a PDF file to the API
and receive the extracted argument graph.
"""

import requests
import json
import sys
from pathlib import Path


def test_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health/")
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on localhost:8000")
        return False


def upload_pdf_and_extract_graph(pdf_path: str, base_url: str = "http://localhost:8000") -> dict:
    """
    Upload a PDF file and extract the argument graph.
    
    Args:
        pdf_path: Path to the PDF file
        base_url: Base URL of the API
        
    Returns:
        Dictionary containing the extraction results
    """
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return None
    
    print(f"📄 Uploading PDF: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(f"{base_url}/extract-results/", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extraction completed successfully!")
            return result
        else:
            print(f"❌ Extraction failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return None


def print_extraction_results(result: dict) -> None:
    """Print the extraction results in a formatted way."""
    if not result or not result.get("success"):
        print("❌ No valid results to display")
        return
    
    print("\n" + "="*60)
    print("📊 EXTRACTION RESULTS")
    print("="*60)
    
    # Document info
    doc_info = result.get("document_info", {})
    print(f"📄 Document: {doc_info.get('filename', 'Unknown')}")
    print(f"📑 Pages: {doc_info.get('total_pages', 0)}")
    print(f"🔗 Content Hash: {doc_info.get('content_hash', 'Unknown')}")
    
    # Graph statistics
    stats = result.get("graph_statistics", {})
    print(f"\n📈 Graph Statistics:")
    print(f"   Total Components: {stats.get('total_components', 0)}")
    print(f"   Total Relationships: {stats.get('total_relationships', 0)}")
    
    # Components by type
    components_by_type = stats.get("components_by_type", {})
    if components_by_type:
        print(f"\n📝 Components by Type:")
        for comp_type, count in components_by_type.items():
            print(f"   {comp_type}: {count}")
    
    # Relationships by type
    relationships_by_type = stats.get("relationships_by_type", {})
    if relationships_by_type:
        print(f"\n🔗 Relationships by Type:")
        for rel_type, count in relationships_by_type.items():
            print(f"   {rel_type}: {count}")
    
    # Sample components
    graph = result.get("argument_graph", {})
    nodes = graph.get("nodes", [])
    if nodes:
        print(f"\n📝 Sample Components:")
        for i, node in enumerate(nodes[:3]):  # Show first 3
            print(f"   {i+1}. {node['type']} (ID: {node['id']}, Page: {node['page']})")
            print(f"      Text: {node['text'][:100]}...")
            print()
    
    # Sample relationships
    edges = graph.get("edges", [])
    if edges:
        print(f"🔗 Sample Relationships:")
        for i, edge in enumerate(edges[:3]):  # Show first 3
            print(f"   {i+1}. {edge['source']} --[{edge['relation']}]--> {edge['target']}")
            print(f"      Page: {edge['page']}")
            print()
    
    print(f"\n💡 Note: This extraction used the enhanced prompts with:")
    print(f"   • Longer, more comprehensive component extraction")
    print(f"   • New component types (Method, Result, Limitation)")
    print(f"   • New relationship types (addresses, compares_to, builds_on, motivates, demonstrates)")


def save_results_to_file(result: dict, output_file: str = "api_extraction_result.json") -> None:
    """Save the extraction results to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")


def main():
    """Main function to test the API."""
    print("🚀 Testing Argument Graph Extraction API")
    print("="*60)
    
    # Test API health
    if not test_api_health():
        return
    
    # Get PDF file path from command line or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for PDF files in the data directory
        data_dir = Path("data/")
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if pdf_files:
            pdf_path = str(pdf_files[0])
            print(f"📄 Using PDF file: {pdf_path}")
        else:
            print("❌ No PDF file specified and no PDF files found in ../data/")
            print("Usage: python test_api.py <path_to_pdf_file>")
            return
    
    # Upload PDF and extract graph
    result = upload_pdf_and_extract_graph(pdf_path)
    
    if result:
        # Print results
        print_extraction_results(result)
        
        # Save results
        save_results_to_file(result)
        
        print("🎉 API test completed successfully!")
    else:
        print("💥 API test failed!")


if __name__ == "__main__":
    main() 