from pathlib import Path

from paper_eval.pipeline.run_pipeline import _process


def test_process_nonexistent_pdf(tmp_path):
    fake = tmp_path / "missing.pdf"
    try:
        _process(fake)
    except FileNotFoundError:
        assert True
    else:
        assert False, "Should raise FileNotFoundError"
