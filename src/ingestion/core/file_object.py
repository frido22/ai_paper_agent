from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date

class PageData(BaseModel):
    """Represents the data extracted from a single page of a PDF."""
    page_number: int
    text: str
    tables: List[List[List[str]]]  # Each table is a list of rows, each row is a list of cells
    
    class Config:
        validate_assignment = True

class FileObject(BaseModel):
    path: Path
    pages: List[PageData]  # List of pages with their respective text and tables
    metadata: Dict[str, str]
    content_hash: str
    
    # Document schema fields
    document_name: str
    document_path: str
    source_id: Optional[int] = None
    start_date_effect: Optional[date] = None
    end_date_effect: Optional[date] = None
    date_publication: Optional[date] = None
    date_ingestion: date = Field(default_factory=date.today)

    class Config:
        arbitrary_types_allowed = True  # allow Path
        validate_assignment = True
    
    @property
    def text(self) -> str:
        """Get all text from all pages concatenated."""
        return "\n".join(page.text for page in self.pages)
    
    @property
    def tables(self) -> List[List[List[str]]]:
        """Get all tables from all pages."""
        all_tables = []
        for page in self.pages:
            all_tables.extend(page.tables)
        return all_tables