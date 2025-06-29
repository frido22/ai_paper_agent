from pathlib import Path

from paper_eval.extractor.pdf_extractor import extract_sections


def test_extract_sections_sample_pdf():
    sample = Path(__file__).parent.parent / "data" / "samples" / "demo.pdf"
    if not sample.exists():
        return  # skip if sample not present
    sections = extract_sections(sample)
    assert isinstance(sections, dict)
