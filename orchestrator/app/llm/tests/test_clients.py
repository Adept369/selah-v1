# app/llm/tests/test_clients.py

import pytest
import sys
import types
import logging
from app.llm.clients import LLMClient

class DummySettings:
    # neither "openai" nor "llama"
    LLM_BACKEND = "not_a_real_backend"
    OPENAI_API_KEY = None
    LLAMA_MODEL_PATH = None

def test_unknown_backend_raises_value_error():
    with pytest.raises(ValueError) as exc:
        LLMClient(DummySettings())
    assert "Unknown LLM_BACKEND" in str(exc.value)

# --- Helpers to stub out backends ------------------------------------------

class DummyOpenAI:
    def __init__(self, api_key):
        # Simulate openai.OpenAI.chat.completions.create(...)
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(
                create=lambda model, messages, **kwargs: types.SimpleNamespace(
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="openai-response"))]
                )
            )
        )

def make_dummy_openai_module():
    mod = types.ModuleType("openai")
    mod.OpenAI = DummyOpenAI
    return mod

def make_dummy_transformers_module():
    # Simulate transformers.pipeline returning a callable
    def pipeline(task, model, device):
        def gen(prompt, **kwargs):
            return [{"generated_text": "llama-response"}]
        return gen

    mod = types.ModuleType("transformers")
    mod.pipeline = pipeline
    return mod

# --- Tests ----------------------------------------------------------------

def test_openai_generate_logs(caplog, monkeypatch):
    # Arrange: stub out openai module before importing LLMClient
    monkeypatch.setitem(sys.modules, "openai", make_dummy_openai_module())
    # Provide minimal settings
    settings = types.SimpleNamespace(LLM_BACKEND="openai", OPENAI_API_KEY="key123")
    client = LLMClient(settings)

    # Capture INFO logs
    caplog.set_level(logging.INFO)

    # Act
    resp = client.generate("hello world", max_tokens=10)

    # Assert
    assert resp == "openai-response"
    # Ensure start log
    assert any("LLMClient.generate start" in rec.getMessage() for rec in caplog.records)
    # Ensure completed log with duration and length
    assert any("LLMClient.generate completed" in rec.getMessage() for rec in caplog.records)


def test_llama_generate_logs(caplog, monkeypatch):
    # Arrange: stub out transformers before importing LLMClient
    monkeypatch.setitem(sys.modules, "transformers", make_dummy_transformers_module())
    # Provide minimal settings
    settings = types.SimpleNamespace(LLM_BACKEND="llama", LLAMA_MODEL_PATH="some/path")
    client = LLMClient(settings)

    caplog.set_level(logging.INFO)

    # Act
    resp = client.generate("foo bar", top_k=5)

    # Assert
    assert resp == "llama-response"
    assert any("LLMClient.generate start" in rec.getMessage() for rec in caplog.records)
    assert any("LLMClient.generate completed" in rec.getMessage() for rec in caplog.records)