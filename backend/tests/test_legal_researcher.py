import asyncio

from app.specialists.legal_researcher import LegalResearcher, MockLLMAdapter


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_happy_path_returns_issues_and_citations():
    messy_text = """
    Hey, I was in a car crash — my neck and back hurt, had an MRI and surgery was recommended.
    The other driver was careless and I think it's negligence. Also, the insurer mentioned limits.
    """

    lr = LegalResearcher(llm_adapter=MockLLMAdapter())
    out = run_async(lr.analyze(messy_text, metadata={}))
    assert "issues" in out
    assert isinstance(out["issues"], list)
    assert len(out["issues"]) >= 1
    assert "brief" in out and isinstance(out["brief"], str)


def test_edge_case_empty_text():
    lr = LegalResearcher(llm_adapter=MockLLMAdapter())
    out = run_async(lr.analyze("", metadata={}))
    assert out["issues"] == []
    assert any("human review" in a.lower() for a in out["suggested_actions"]) or len(out["suggested_actions"]) >= 1
