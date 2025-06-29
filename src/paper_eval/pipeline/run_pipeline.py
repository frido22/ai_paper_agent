from __future__ import annotations
"""Main orchestration script (Person E).

Usage (CLI):
    python -m paper_eval.pipeline.run_pipeline /path/to/paper.pdf
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

from typer import Typer, echo

from paper_eval.extractor.pdf_extractor import extract_sections
from paper_eval.parser.section_parser import get_target_sections
from paper_eval.evaluator.consistency_evaluator import score
from paper_eval.figmatcher.figure_matcher import supports

app = Typer(add_help_option=True)


def _process(pdf_path: Path) -> Dict[str, Any]:
    sections = extract_sections(pdf_path)
    results, conclusion, fig_caps = get_target_sections(sections)

    numeric_score, justification = score(results, conclusion)
    support_map = supports(conclusion, fig_caps)

    return {
        "pdf": str(pdf_path),
        "score": numeric_score,
        "justification": justification,
        "fig_support": support_map,
    }


@app.command()
def main(pdf: str):
    """Run evaluation on *pdf* and dump JSON to stdout."""
    path = Path(pdf)
    if not path.exists():
        echo(f"File not found: {pdf}", err=True)
        raise SystemExit(1)

    out = _process(path)
    echo(json.dumps(out, indent=2))


if __name__ == "__main__":
    app()
