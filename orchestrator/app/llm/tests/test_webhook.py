# orchestrator/app/tests/test_webhook.py

import pytest
from fastapi.testclient import TestClient
from app.main import app, master
from app.core.config import settings

@pytest.fixture(autouse=True)
def stub_master_run(monkeypatch):
    """
    Replace MasterAgent.run with a dummy coroutine so we don't
    depend on external LLM calls in our smoke test.
    """
    async def dummy_run(update):
        return "✅ dummy response"
    monkeypatch.setattr(master, "run", dummy_run)

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_webhook_returns_dummy_response():
    client = TestClient(app)
    payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "chat": {"id": 999, "type": "private"},
            "text": "anything"
        }
    }
    headers = {
        "X-Telegram-Bot-Api-Secret-Token": settings.WEBHOOK_SECRET
    }
    r = client.post("/webhook", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    # Should return non-null status and our dummy reply
    assert body["status"] == "ok"
    assert body["reply"] == "✅ dummy response"
