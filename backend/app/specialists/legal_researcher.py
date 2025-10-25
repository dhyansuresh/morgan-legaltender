import re
from typing import List

from ..schemas import Citation


class LLMAdapter:
    """Abstract adapter interface for an LLM. Implementations should provide `complete` method.

    We keep this abstract so production keys/calls are isolated and tests can use a Mock.
    """

    async def complete(self, prompt: str) -> str:  # pragma: no cover - adapter implemented elsewhere
        raise NotImplementedError()


class MockLLMAdapter(LLMAdapter):
    async def complete(self, prompt: str) -> str:
        # Very small deterministic mock that echoes prompt summary lines.
        return "MockLLM: summarized research findings."


class LegalResearcher:
    """Legal Researcher agent: analyze messy text and return issues, citations, and actions.

    Contract (simple):
    - Input: free text (emails, transcripts, notes)
    - Output: dict with issues (strings), citations (Citation), suggested_actions, brief

    Error modes: returns empty lists for no findings.
    """

    def __init__(self, llm_adapter: LLMAdapter = None):
        self.llm = llm_adapter or MockLLMAdapter()

    def _extract_issues(self, text: str) -> List[str]:
        issues = set()
        t = text.lower()
        # very simple key phrase heuristics — placeholders for ML/LLM
        if re.search(r"\bneck|back|head|arm|leg|fracture|broken\b", t):
            issues.add("Injury / bodily harm described — check medical records and bills")
        if re.search(r"\bdriv|accident|crash|collision\b", t):
            issues.add("Auto accident — possible third-party liability and PIP/UM coverage checks")
        if re.search(r"\bnegligence|careless|reckless\b", t):
            issues.add("Allegation of negligence — identify potential duty, breach, causation")
        if re.search(r"\bsettle|settlement|limits|tender\b", t):
            issues.add("Settlement / tender language — prepare demand and policy analysis")
        if re.search(r"\bMRI|x-?ray|ct scan|prescription|surgery|therapy|pt\b", t):
            issues.add("Medical treatments referenced — gather records and billing codes")
        return list(issues)

    def _find_citations(self, text: str) -> List[Citation]:
        # Mock citation finder: returns a couple of representative citations when 'negligence' appears
        t = text.lower()
        results = []
        if "negligence" in t or "duty" in t:
            results.append(Citation(title="Smith v. Jones", citation="123 A.2d 456 (Fla. 1990)", url=None))
            results.append(Citation(title="Comparative Negligence Overview", citation=None, url="https://example.com/comp-negligence"))
        return results

    async def analyze(self, text: str, metadata: dict = None) -> dict:
        issues = self._extract_issues(text)
        citations = self._find_citations(text)
        suggested_actions = []
        if issues:
            suggested_actions.append("Collect medical records and itemized bills")
            suggested_actions.append("Run legal research for negligence and damages")
        else:
            suggested_actions.append("Flag for human review — not enough info to act")

        # Use LLM adapter to draft a short research brief (mocked in tests)
        prompt = f"Summarize key legal issues and next steps for the following text:\n\n{text}\n"
        brief = await self.llm.complete(prompt)

        return {
            "issues": issues,
            "citations": [c.dict() for c in citations],
            "suggested_actions": suggested_actions,
            "brief": brief,
        }
