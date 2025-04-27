# orchestrator/tests/test_config.py

import os
import pytest
from pydantic import ValidationError

from app.core.config import Settings

# list of all required env var names from Settings
REQUIRED = [
    "TELEGRAM_TOKEN",
    "WEBHOOK_SECRET",
    "RABBITMQ_URL",
    "N8N_WEBHOOK_URL",
    "N8N_USER",
    "N8N_PASSWORD",
    "CASELAW_PINECONE_API_KEY",
    "CASELAW_PINECONE_ENVIRONMENT",
    "CASELAW_PINECONE_INDEX",
    "MEMO_PINECONE_API_KEY",
    "MEMO_PINECONE_ENVIRONMENT",
    "MEMO_PINECONE_INDEX",
    "PINECONE_API_KEY",
    "PINECONE_ENV",
]

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # clear all relevant env vars before each test
    for var in REQUIRED + ["LLM_BACKEND", "OPENAI_API_KEY", "LLAMA_MODEL_PATH", "SOME_EXTRA"]:
        monkeypatch.delenv(var, raising=False)
    yield
    # no teardown needed

def test_success_with_all_required(monkeypatch):
    # populate all REQUIRED env vars
    for var in REQUIRED:
        monkeypatch.setenv(var, f"val_for_{var.lower()}")
    # optional LLM settings
    monkeypatch.setenv("LLM_BACKEND", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-openai-key")

    cfg = Settings()  # should not raise
    # spot check a couple
    assert cfg.TELEGRAM_TOKEN == "val_for_telegram_token"
    assert cfg.CASELAW_PINECONE_INDEX == "val_for_caselaw_pinecone_index"
    # extra vars are ignored
    monkeypatch.setenv("SOME_EXTRA", "ignored")
    cfg2 = Settings()
    assert not hasattr(cfg2, "SOME_EXTRA")

def test_missing_one_required_raises(monkeypatch):
    # set all except one
    for var in REQUIRED:
        if var != "TELEGRAM_TOKEN":
            monkeypatch.setenv(var, "foo")
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "TELEGRAM_TOKEN" in str(excinfo.value)

def test_missing_many_required_raises(monkeypatch):
    # set none
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    # should mention at least two missing fields
    msg = str(excinfo.value)
    assert "TELEGRAM_TOKEN" in msg
    assert "WEBHOOK_SECRET" in msg
