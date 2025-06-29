from ingestion.core.file_registry import FileRegistry
from ingestion.core.file_scanner import FolderScanner
from ingestion.core.file_object import FileObject
from ingestion.utils.pdf_extraction import PDFExtractor
from ingestion.utils.hashing import Hasher
from ingestion.utils.file_loader import FileLoader
from ingestion.pipeline.processor import Processor
from datetime import date
from pathlib import Path

def run_pipeline(force_reprocess: bool = False, file_path: Path = None):
    scanner = FolderScanner(Path("data"))
    registry = FileRegistry()
    processor = Processor()
    file_objs = []

    # If a specific file path is provided, only process that file
    if file_path is not None:
        if file_path.exists() and file_path.suffix.lower() == '.pdf':
            paths_to_process = [file_path]
        else:
            print(f"File {file_path} does not exist or is not a PDF file.")
            return []
    else:
        # Process all PDF files in the data folder
        paths_to_process = scanner.get_pdf_paths()

    for path in paths_to_process:
        # Create initial metadata
        metadata = {
            "name": path.name,
            "size": str(path.stat().st_size),  # serialized to str for Pydantic validation
        }
        
        # Hash metadata first to check for duplicates
        metadata_hash = Hasher.hash_content(metadata)
        
        if registry.is_new(metadata_hash) or force_reprocess:
            # Extract text and tables page by page
            pages_data = PDFExtractor.extract_text_and_tables(path)
            
            # Create FileObject with page-based data
            file_obj = FileObject(
                path=path,
                pages=pages_data,
                metadata=metadata,
                content_hash=metadata_hash,
                document_name=path.name,
                document_path=str(path),
                date_ingestion=date.today()  # Set ingestion date to today
            )

            file_objs.append(file_obj)
            
            # Process the file and get the Document instance
            document = processor.handle(file_obj)
            registry.register(metadata_hash, file_obj)  # Register with file object data
            
            print(f"Processed new file: {path.name} with {len(pages_data)} pages")
            print(f"Document created with ID: {document.document_id if hasattr(document, 'document_id') else 'Not saved to DB'}")
        else:
            # Load stored FileObject instead of skipping
            print(f"Loading previously processed file: {path.name}")
            stored_file_obj = FileLoader.load_stored_file_object(metadata_hash)
            
            if stored_file_obj is not None:
                file_objs.append(stored_file_obj)
                print(f"Successfully loaded stored file: {path.name} with {len(stored_file_obj.pages)} pages")
            else:
                print(f"Warning: Could not load stored file for {path.name}, will reprocess")
                # Fallback to reprocessing if stored file can't be loaded
                pages_data = PDFExtractor.extract_text_and_tables(path)
                
                file_obj = FileObject(
                    path=path,
                    pages=pages_data,
                    metadata=metadata,
                    content_hash=metadata_hash,
                    document_name=path.name,
                    document_path=str(path),
                    date_ingestion=date.today()
                )

                file_objs.append(file_obj)
                document = processor.handle(file_obj)
                registry.register(metadata_hash, file_obj)
                
                print(f"Reprocessed file: {path.name} with {len(pages_data)} pages")
    
    return file_objs

def load_stored_file(content_hash: str) -> FileObject:
    """
    Load a specific stored file by its content hash.
    
    Args:
        content_hash: The content hash of the file to load
        
    Returns:
        FileObject if found, None otherwise
    """
    return FileLoader.load_stored_file_object(content_hash)

def get_all_stored_files() -> list[FileObject]:
    """
    Load all stored files from the processed directory.
    
    Returns:
        List of FileObject instances
    """
    content_hashes = FileLoader.get_available_stored_files()
    file_objects = []
    
    for content_hash in content_hashes:
        file_obj = FileLoader.load_stored_file_object(content_hash)
        if file_obj is not None:
            file_objects.append(file_obj)
    
    return file_objects

def main():
    file_objs = run_pipeline()

if __name__ == "__main__":
    main()