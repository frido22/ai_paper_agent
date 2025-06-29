import json
from pathlib import Path
from typing import Optional, List
from datetime import date
from ..core.file_object import FileObject, PageData

class FileLoader:
    @staticmethod
    def load_stored_file_object(content_hash: str, processed_dir: Path = Path("data/processed")) -> Optional[FileObject]:
        """
        Load a stored FileObject from the processed data directory.
        
        Args:
            content_hash: The content hash of the file to load
            processed_dir: Directory containing processed files
            
        Returns:
            FileObject if found, None otherwise
        """
        file_dir = processed_dir / content_hash
        
        if not file_dir.exists():
            return None
            
        try:
            # Load pages data
            pages_file = file_dir / "pages.json"
            if not pages_file.exists():
                return None
                
            with open(pages_file, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)
            
            # Convert back to PageData objects
            pages = []
            for page_dict in pages_data:
                page_data = PageData(
                    page_number=page_dict["page_number"],
                    text=page_dict["text"],
                    tables=page_dict["tables"]
                )
                pages.append(page_data)
            
            # Load metadata summary for file object creation
            metadata_file = file_dir / "metadata_summary.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata_summary = json.load(f)
                
                # Extract file metadata
                file_metadata = metadata_summary.get("file_metadata", {})
                document_info = metadata_summary.get("document_info", {})
                
                # Create FileObject
                file_obj = FileObject(
                    path=Path(document_info.get("document_path", "")),
                    pages=pages,
                    metadata=file_metadata,
                    content_hash=content_hash,
                    document_name=document_info.get("document_name", ""),
                    document_path=document_info.get("document_path", ""),
                    date_ingestion=date.fromisoformat(document_info.get("date_ingestion", date.today().isoformat()))
                )
                
                return file_obj
            else:
                # Fallback: create minimal FileObject if metadata file doesn't exist
                file_obj = FileObject(
                    path=file_dir / "document.pdf",  # Placeholder path
                    pages=pages,
                    metadata={"name": f"document_{content_hash[:8]}", "size": "0"},
                    content_hash=content_hash,
                    document_name=f"document_{content_hash[:8]}",
                    document_path=str(file_dir / "document.pdf"),
                    date_ingestion=date.today()
                )
                return file_obj
                
        except Exception as e:
            print(f"Error loading stored file object for hash {content_hash}: {e}")
            return None

    @staticmethod
    def get_available_stored_files(processed_dir: Path = Path("data/processed")) -> List[str]:
        """
        Get list of content hashes for all available stored files.
        
        Args:
            processed_dir: Directory containing processed files
            
        Returns:
            List of content hash strings
        """
        if not processed_dir.exists():
            return []
            
        content_hashes = []
        for item in processed_dir.iterdir():
            if item.is_dir() and (item / "pages.json").exists():
                content_hashes.append(item.name)
                
        return content_hashes 