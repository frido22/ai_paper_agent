from __future__ import annotations
"""Naive figure–claim matcher (Person D).

For v1 we simply keyword-match fig numbers in conclusion sentences.
"""

from typing import Dict, List
import re

__all__ = ["supports"]

_FIG_REF_PATTERN = re.compile(r"figure\s*(\d+)", re.I)


def supports(conclusion: str, figure_captions: List[str]) -> Dict[str, bool]:
    """Return mapping claim_sentence → supported? (bool).

    Currently: a claim is *supported* if it references a figure number that
    exists in `figure_captions` list.
    """
    claims = [c.strip() for c in re.split(r"[.!?]", conclusion) if c.strip()]

    # build simple lookup of available numbers from captions
    available = set()
    for cap in figure_captions:
        m = _FIG_REF_PATTERN.search(cap)
        if m:
            available.add(m.group(1))

    result: Dict[str, bool] = {}
    for c in claims:
        refs = _FIG_REF_PATTERN.findall(c)
        result[c] = any(num in available for num in refs)
    return result
