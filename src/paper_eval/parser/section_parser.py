from __future__ import annotations
"""Section detection and cleaning (Person B).

Takes raw section dict from `extractor.extract_sections` and
returns cleaned text blocks ready for the evaluator.
"""

from typing import Dict, Tuple, List
import re

__all__ = ["get_target_sections"]


def _clean(text: str) -> str:
    """Normalize whitespace, drop excessive line breaks."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_target_sections(sections: Dict[str, str]) -> Tuple[str, str, List[str]]:
    """Return (results, conclusion, figure_captions).

    If a section is missing, returns an empty string/list instead of raising.
    """
    results = _clean(sections.get("results", ""))
    conclusion = _clean(sections.get("conclusion", ""))

    # crude capture of figure captions present in any section text
    fig_caps = []
    fig_pat = re.compile(r"figure\s*\d+[:.\s](.+?)(?=figure|$)", re.I | re.S)
    for sec_text in sections.values():
        for cap in fig_pat.findall(sec_text):
            fig_caps.append(_clean(cap))

    return results, conclusion, fig_caps
