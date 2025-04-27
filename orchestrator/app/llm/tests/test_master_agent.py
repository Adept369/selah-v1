# app/orchestration/tests/test_master_agent.py

import pytest

from app.orchestration.master_agent import MasterAgent

class DummyLLM:
    def generate(self, prompt, **kwargs):
        return "dummy response"

@pytest.fixture
def master():
    return MasterAgent(llm_client=DummyLLM())

@pytest.mark.parametrize("text,expected", [
    ("Tell me about tribal sovereignty precedent", "case_law_scholar"),
    ("Please draft a memo on quarterly earnings", "memo_drafter"),
    ("Remind me tomorrow at 9am", "n8n_scheduler"),
    ("What’s the weather like?", "help"),
])
def test_classify_intent(master, text, expected):
    assert master.classify_intent(text) == expected

def test_parse_strips_to_full_text(master):
    key, query = master.parse("Explain tribal law in detail")
    assert key == "case_law_scholar"
    assert query == "Explain tribal law in detail"

@pytest.mark.asyncio
async def test_run_routes_and_invokes(monkeypatch, master):
    # stub out registry to contain one fake agent
    class FakeAgent:
        def __init__(self):
            self.called_with = None
        def run(self, q):
            self.called_with = q
            return "FAKE_RESULT"

    # replace master.registry and AGENT_REGISTRY lookup
    monkeypatch.setitem(master.registry, "fake", FakeAgent())
    # also ensure we test behavior when classify_intent returns our fake key
    monkeypatch.setattr(master, "classify_intent", lambda t: "fake")

    # build a fake Telegram update
    update = {"message": {"text": "anything", "chat": {"id": 1234}}}
    reply = await master.run(update)
    assert reply == "FAKE_RESULT"
    # ensure the agent got the right query
    assert list(master.registry["fake"].called_with for _ in [None])[0] == "anything"
