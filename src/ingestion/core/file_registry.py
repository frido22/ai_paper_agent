import json
from pathlib import Path
from typing import Set, Dict, Optional
from ..core.file_object import FileObject

class FileRegistry:
    def __init__(self, registry_file: Path = Path("data/registry.json")):
        self.registry_file = registry_file
        self.processed_data: Dict[str, Dict] = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict]:
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_registry(self):
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.processed_data, f, indent=2, default=str)

    def is_new(self, content_hash: str) -> bool:
        return content_hash not in self.processed_data

    def register(self, content_hash: str, file_obj: FileObject):
        """Register a file object with its content hash"""
        # Store essential file object data
        file_data = {
            "document_name": file_obj.document_name,
            "document_path": file_obj.document_path,
            "content_hash": file_obj.content_hash,
            "date_ingestion": file_obj.date_ingestion.isoformat(),
            "metadata": file_obj.metadata,
            "pages_count": len(file_obj.pages),
            "total_text_length": len(file_obj.text),
            "total_tables_count": len(file_obj.tables),
            "processed_output_dir": f"data/processed/{content_hash}"
        }
        
        self.processed_data[content_hash] = file_data
        self._save_registry()

    def get_stored_file_data(self, content_hash: str) -> Optional[Dict]:
        """Retrieve stored file data for a given content hash"""
        return self.processed_data.get(content_hash)

    def get_all_processed_files(self) -> Dict[str, Dict]:
        """Get all processed files data"""
        return self.processed_data.copy()
