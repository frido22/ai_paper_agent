from ..core.file_object import FileObject
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ..common.schemas import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Processor:
    def __init__(self, output_dir: Path = Path("data/processed")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def handle(self, file_obj: FileObject):
        """
        Process a file object by:
        1. Creating a Document instance
        2. Extracting and storing page-based content
        3. Creating a metadata summary
        """
        logger.info(f"Processing file: {file_obj.path.name}")
        
        # Create a unique output directory for this file
        file_output_dir = self.output_dir / file_obj.content_hash
        file_output_dir.mkdir(exist_ok=True)

        # Create Document instance
        document = Document(
            document_name=file_obj.document_name,
            document_path=file_obj.document_path,
            source_id=file_obj.source_id,
            start_date_effect=file_obj.start_date_effect,
            end_date_effect=file_obj.end_date_effect,
            date_publication=file_obj.date_publication,
            date_ingestion=file_obj.date_ingestion
        )

        # Process and store page-based content
        self._process_pages(file_obj, file_output_dir)
        
        # Create and store metadata summary
        self._create_metadata_summary(file_obj, document, file_output_dir)
        
        logger.info(f"Successfully processed file: {file_obj.path.name}")
        return document

    def _process_pages(self, file_obj: FileObject, output_dir: Path):
        """Process and store the page-based content"""
        # Create structured JSON with all pages
        pages_data = []
        
        for page in file_obj.pages:
            page_data = {
                "page_number": page.page_number,
                "text": page.text,
                "tables": page.tables,
                "text_stats": {
                    "word_count": len(page.text.split()),
                    "char_count": len(page.text),
                    "line_count": len(page.text.splitlines()),
                    "table_count": len(page.tables)
                }
            }
            pages_data.append(page_data)
        
        # Store the complete page-based structure
        with open(output_dir / "pages.json", "w", encoding="utf-8") as f:
            json.dump(pages_data, f, indent=2, ensure_ascii=False)
        
        # Store overall text statistics
        overall_stats = {
            "total_pages": len(file_obj.pages),
            "total_word_count": len(file_obj.text.split()),
            "total_char_count": len(file_obj.text),
            "total_line_count": len(file_obj.text.splitlines()),
            "total_table_count": sum(len(page.tables) for page in file_obj.pages),
            "pages_with_tables": sum(1 for page in file_obj.pages if page.tables),
            "pages_with_text": sum(1 for page in file_obj.pages if page.text.strip())
        }
        
        with open(output_dir / "text_stats.json", "w") as f:
            json.dump(overall_stats, f, indent=2)

    def _create_metadata_summary(self, file_obj: FileObject, document: Document, output_dir: Path):
        """Create and store a comprehensive metadata summary"""
        summary: Dict[str, Any] = {
            "document_info": {
                "document_name": document.document_name,
                "document_path": document.document_path,
                "source_id": document.source_id,
                "start_date_effect": document.start_date_effect.isoformat() if document.start_date_effect else None,
                "end_date_effect": document.end_date_effect.isoformat() if document.end_date_effect else None,
                "date_publication": document.date_publication.isoformat() if document.date_publication else None,
                "date_ingestion": document.date_ingestion.isoformat()
            },
            "file_metadata": file_obj.metadata,
            "content_hash": file_obj.content_hash,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_stats": {
                "total_pages": len(file_obj.pages),
                "pages_with_tables": sum(1 for page in file_obj.pages if page.tables),
                "pages_with_text": sum(1 for page in file_obj.pages if page.text.strip()),
                "total_table_count": sum(len(page.tables) for page in file_obj.pages),
                "total_text_length": len(file_obj.text),
            }
        }
        
        with open(output_dir / "metadata_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
