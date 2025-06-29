#!/usr/bin/env python3
"""
Example usage of the enhanced ingestion pipeline with stored pages objects.
"""

from pathlib import Path
from ingestion.ingest import run_pipeline, load_stored_file, get_all_stored_files
from ingestion.core.file_registry import FileRegistry

def main():
    print("=== Research Paper Scanner - Enhanced Ingestion Example ===\n")
    
    # 1. Run the pipeline (processes new files, loads stored files)
    print("1. Running ingestion pipeline...")
    file_objects = run_pipeline()
    
    print(f"\nProcessed {len(file_objects)} files total\n")
    
    # 2. Display information about each file
    for i, file_obj in enumerate(file_objects, 1):
        print(f"File {i}: {file_obj.document_name}")
        print(f"  - Pages: {len(file_obj.pages)}")
        print(f"  - Total text length: {len(file_obj.text):,} characters")
        print(f"  - Total tables: {len(file_obj.tables)}")
        print(f"  - Content hash: {file_obj.content_hash[:16]}...")
        print()
    
    # 3. Demonstrate loading specific stored files
    print("2. Demonstrating stored file loading...")
    registry = FileRegistry()
    all_processed = registry.get_all_processed_files()
    
    if all_processed:
        # Load the first stored file as an example
        first_hash = list(all_processed.keys())[0]
        stored_file = load_stored_file(first_hash)
        
        if stored_file:
            print(f"Successfully loaded stored file: {stored_file.document_name}")
            print(f"  - Pages: {len(stored_file.pages)}")
            print(f"  - Text length: {len(stored_file.text):,} characters")
            print(f"  - Tables: {len(stored_file.tables)}")
            
            # Show first page content preview
            if stored_file.pages:
                first_page = stored_file.pages[0]
                text_preview = first_page.text[:200] + "..." if len(first_page.text) > 200 else first_page.text
                print(f"  - First page text preview: {text_preview}")
                print(f"  - First page tables: {len(first_page.tables)}")
        else:
            print("Failed to load stored file")
    else:
        print("No processed files found in registry")
    
    # 4. Demonstrate loading all stored files
    print("\n3. Loading all stored files...")
    all_stored = get_all_stored_files()
    print(f"Found {len(all_stored)} stored files")
    
    # 5. Show detailed page information for first file
    if file_objects:
        print(f"\n4. Detailed page analysis for: {file_objects[0].document_name}")
        for i, page in enumerate(file_objects[0].pages, 1):
            print(f"  Page {i}:")
            print(f"    - Text: {len(page.text):,} characters")
            print(f"    - Tables: {len(page.tables)}")
            if page.tables:
                for j, table in enumerate(page.tables, 1):
                    print(f"      Table {j}: {len(table)} rows x {len(table[0]) if table else 0} columns")
            print()

if __name__ == "__main__":
    main() 