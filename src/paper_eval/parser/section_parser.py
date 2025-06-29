from __future__ import annotations
"""
Section detection and cleaning (Person B).

New in this version
-------------------
* Accepts *either* a ready-made `{"results": …, "conclusion": …}` dict
  **or** the raw page list emitted by the extractor.
* Minimal, heuristic splitter that looks for the first occurrence of
  “RESULTS” and “CONCLUSION” (case-insensitive) in the concatenated text.
* Everything else – whitespace normalisation and figure-caption capture –
  is unchanged.
"""

from typing import Dict, Tuple, List, Sequence, Any
import re
import os
from dotenv import load_dotenv            # pip install python-dotenv
import openai                             # pip install openai

load_dotenv()                             # reads .env at project root
openai.api_key = os.getenv("OPENAI_API_KEY")  # raises if missing

__all__ = ["get_target_sections"]

# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Collapse all whitespace → single spaces and strip ends."""
    return re.sub(r"\s+", " ", text).strip()




def _pages_to_sections(pages: Sequence[Dict[str, Any]]) -> Dict[str, str]:
    """
    Find the first 'results' and 'conclusion' headings—robust to:
      • optional leading digits ('7 ')
      • extra words stuck on the end ('conclusionandoutlook')
      • any amount of spaces or punctuation around the keyword
    and return the text *after the newline* that ends each heading.
    """
    full_text = "\n".join(p.get("text", "") for p in pages)

    # Regex that matches an entire heading line
    #   ^\s*\d*\s*   optional numbering
    #   (results|conclusion)   capture the keyword
    #   [^\n]*       any junk until the newline
    heading_re = re.compile(r"^\s*\d*\s*(results|conclusion)[^\n]*",
                            flags=re.I | re.M)

    hits = list(heading_re.finditer(full_text))
    if not hits:
        return {}          # no headings at all

    # map keyword → (start_of_body, end_of_body)
    bounds: Dict[str, Tuple[int, int]] = {}
    for i, m in enumerate(hits):
        key = m.group(1).lower()         # "results" or "conclusion"
        body_start = full_text.find("\n", m.end()) + 1  # right after newline
        body_end   = hits[i + 1].start() if i + 1 < len(hits) else len(full_text)
        bounds.setdefault(key, (body_start, body_end))

    return {k: full_text[s:e] for k, (s, e) in bounds.items()}

# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def get_target_sections(
    raw: Dict[str, str] | Sequence[Dict[str, Any]]
) -> Tuple[str, str, List[str]]:
    """
    Return `(results, conclusion, figure_captions)`.

    Parameters
    ----------
    raw
        • a dict that already maps section names → raw text
          (previous behaviour), **or**
        • the list of page dicts produced by the extractor
          (each with `"text"`).

    Missing sections return "" (results / conclusion) or [] (captions),
    never raises.
    """
    # If the caller passed page-records, convert them first
    if isinstance(raw, (list, tuple)):
        sections = _pages_to_sections(raw)
    else:
        sections = raw

    results    = _clean(sections.get("results", ""))
    conclusion = _clean(sections.get("conclusion", ""))

    # crude capture of figure captions anywhere in the provided text
    fig_caps: List[str] = []
    fig_pat = re.compile(r"figure\s*\d+[:.\s](.+?)(?=figure|\Z)",
                         flags=re.I | re.S)
    for sec_text in sections.values():
        fig_caps += [_clean(cap) for cap in fig_pat.findall(sec_text)]

    return results, conclusion, fig_caps
