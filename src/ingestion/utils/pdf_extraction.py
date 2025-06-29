from pathlib import Path
import pdfplumber
import pandas as pd
from typing import Tuple, List, Dict, Any
import logging
import re
from ingestion.core.file_object import PageData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    @staticmethod
    def extract_text_and_tables(pdf_path: Path) -> List[PageData]:
        """
        Extract text and tables from a PDF file page by page using pdfplumber.
        Returns a list of PageData objects, one for each page.
        """
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract content from each page separately
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text from the page
                    page_text = page.extract_text() or ""
                    
                    # Extract tables from the page
                    page_tables = page.extract_tables() or []
                    cleaned_tables = []
                    
                    for table in page_tables:
                        # Clean and validate the table
                        cleaned_table = PDFExtractor._clean_table(table)
                        if cleaned_table is not None:
                            cleaned_tables.append(cleaned_table)
                    
                    # Create PageData object for this page
                    page_data = PageData(
                        page_number=page_num,
                        text=page_text,
                        tables=cleaned_tables
                    )
                    pages_data.append(page_data)
                    
                    logger.info(f"Extracted page {page_num}: {len(page_text)} chars, {len(cleaned_tables)} tables")
                                
        except Exception as e:
            logger.warning(f"Could not extract content from {pdf_path}: {e}")
            return []
            
        return pages_data

    @staticmethod
    def extract_text_and_tables_legacy(pdf_path: Path) -> Tuple[str, List[List[List[str]]]]:
        """
        Legacy method for backward compatibility.
        Extract text and tables from a PDF file using pdfplumber.
        Returns a tuple of (text, tables) where tables is a list of tables,
        and each table is a list of rows.
        """
        text = ""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                    
                    # Extract tables from the page
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            # Clean and validate the table
                            cleaned_table = PDFExtractor._clean_table(table)
                            if cleaned_table is not None:
                                tables.append(cleaned_table)
                                
        except Exception as e:
            logger.warning(f"Could not extract content from {pdf_path}: {e}")
            return text, []
            
        return text, tables

    @staticmethod
    def _clean_cell(value: Any) -> str:
        """
        Clean a single cell value.
        """
        if value is None:
            return ''
            
        # Convert to string and clean
        value = str(value).strip()
        
        # Remove multiple spaces
        value = re.sub(r'\s+', ' ', value)
        
        return value

    @staticmethod
    def _clean_table(table: List[List[Any]]) -> List[List[str]]:
        """
        Clean and validate a table.
        Returns None if the table is invalid or empty after cleaning.
        """
        if not table or not table[0]:
            return None
            
        # Convert all cells to strings and clean them
        cleaned_table = []
        for row in table:
            cleaned_row = [PDFExtractor._clean_cell(cell) for cell in row]
            # Skip rows that are all empty
            if any(cell for cell in cleaned_row):
                cleaned_table.append(cleaned_row)
                
        if not cleaned_table:
            return None
            
        # Remove columns that are all empty
        if cleaned_table:
            # Transpose to work with columns
            cols = list(zip(*cleaned_table))
            # Keep only non-empty columns
            non_empty_cols = [col for col in cols if any(cell for cell in col)]
            if non_empty_cols:
                # Transpose back to rows
                cleaned_table = list(zip(*non_empty_cols))
            else:
                return None
                
        # Convert to list of lists
        return [list(row) for row in cleaned_table]

    @staticmethod
    def _remove_duplicate_tables(tables: List[List[List[str]]]) -> List[List[List[str]]]:
        """
        Remove duplicate tables based on content.
        """
        unique_tables = []
        seen_contents = set()
        
        for table in tables:
            # Convert table to string representation for comparison
            table_str = str(table)
            
            if table_str not in seen_contents:
                seen_contents.add(table_str)
                unique_tables.append(table)
        
        return unique_tables

    @staticmethod
    def _is_valid_table(table: pd.DataFrame) -> bool:
        """
        Check if a table is valid (has content and structure).
        """
        if table.empty:
            return False
            
        # Check if table has at least 2 rows and 2 columns
        if table.shape[0] < 2 or table.shape[1] < 2:
            return False
            
        # Check if table has any non-empty content
        if (table == '').all().all():
            return False
            
        return True
