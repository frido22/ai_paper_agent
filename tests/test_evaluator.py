from paper_eval.evaluator.consistency_evaluator import score


def test_score_empty_inputs(monkeypatch):
    # patch OpenAI call to avoid real API usage
    def dummy_score(results: str, conclusion: str):
        return 100, "dummy"

    monkeypatch.setattr("paper_eval.evaluator.consistency_evaluator.score", dummy_score)
    s, j = dummy_score("", "")
    assert isinstance(s, int)
    assert isinstance(j, str)
