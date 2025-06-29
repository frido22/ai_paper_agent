from __future__ import annotations

"""PDF extraction utilities (Person A).

This file stays <400 LOC. Uses PyMuPDF (fitz) to pull raw text
and split on common section headings.  All heavy lifting lives in
`extract_sections`, the only public symbol.
"""

from pathlib import Path
from typing import Dict, List
import re

import fitz  # PyMuPDF
from tqdm import tqdm

# Common section names we care about
_SECTION_HINTS: List[str] = [
    "abstract",
    "introduction",
    "methods",
    "materials and methods",
    "results",
    "discussion",
    "conclusion",
    "references",
]

_SECTION_PATTERN = re.compile(r"^\s*(%s)\b[:\s]*$" % "|".join(_SECTION_HINTS), re.I)


def _extract_text(pdf_path: Path) -> str:
    """Return the full text of *pdf_path* using PyMuPDF."""
    doc = fitz.open(pdf_path)
    out: List[str] = []
    for page in doc:
        out.append(page.get_text())
    return "\n".join(out)


def _split_into_sections(raw_text: str) -> Dict[str, str]:
    """Very naive splitter that uses regex to find section headings.

    Returns a dict mapping lower-cased section name → text block.
    """
    sections: Dict[str, List[str]] = {}
    current_section = "other"
    sections[current_section] = []

    for line in raw_text.splitlines():
        m = _SECTION_PATTERN.match(line)
        if m:
            current_section = m.group(1).lower()
            sections.setdefault(current_section, [])
            continue
        sections[current_section].append(line)

    # join lists to strings
    return {sec: "\n".join(lines).strip() for sec, lines in sections.items()}


def extract_sections(pdf_path: str | Path) -> Dict[str, str]:
    """Public helper used by downstream modules.

    Parameters
    ----------
    pdf_path : str | Path
        Path to a PDF file.

    Returns
    -------
    Dict[str, str]
        Mapping of *section name* → text.  At minimum may contain
        keys like "results" and "conclusion" if they were detected.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    raw_text = _extract_text(pdf_path)
    sections = _split_into_sections(raw_text)
    return sections

__all__ = ["extract_sections"]
