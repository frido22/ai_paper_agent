"""
Core components for the ingestion package.

This module provides the fundamental classes for file handling, scanning, and tracking
in the document ingestion pipeline.
"""

from .file_object import FileObject
from .file_registry import FileRegistry
from .file_scanner import FolderScanner

__all__ = [
    'FileObject',
    'FileRegistry',
    'FolderScanner'
]
