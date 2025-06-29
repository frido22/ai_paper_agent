from paper_eval.parser.section_parser import get_target_sections


def test_get_target_sections_missing():
    sections = {}
    results, conclusion, fig_caps = get_target_sections(sections)
    assert results == ""
    assert conclusion == ""
    assert fig_caps == []
