"""Pruebas del SDK Groq sin realizar llamadas externas."""

import json
from types import SimpleNamespace

import pytest

from ai_support_engine.errors import EngineConfigurationError, EngineExecutionError
from ai_support_engine.generative import classify_generative
from ai_support_engine.models import Category, Mode


def provider_payload(**overrides):
    result = {
        "category": "ACCESS",
        "priority": "MEDIUM",
        "response": "Utiliza la recuperación de contraseña.",
        "requiresHumanReview": False,
        "mode": "generative",
    }
    result.update(overrides)
    return result


def fake_completion(payload):
    content = json.dumps(payload) if not isinstance(payload, str) else payload
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def mock_client(monkeypatch, completion=None, failure=None):
    class FakeCompletions:
        def create(self, **kwargs):
            if failure is not None:
                raise failure
            assert kwargs["response_format"] == {"type": "json_object"}
            assert kwargs["messages"][0]["role"] == "system"
            assert kwargs["messages"][1]["role"] == "user"
            return completion

    class FakeGroq:
        def __init__(self, **kwargs):
            assert kwargs["api_key"] == "test-key"
            assert kwargs["timeout"] == 30.0
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr("ai_support_engine.generative.Groq", FakeGroq)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(EngineConfigurationError):
        classify_generative("Mensaje")


def test_missing_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "")
    with pytest.raises(EngineConfigurationError):
        classify_generative("Mensaje")


def test_contract_and_sdk_call(monkeypatch):
    mock_client(monkeypatch, fake_completion(provider_payload()))
    result = classify_generative("No puedo iniciar sesión")
    assert result.category is Category.ACCESS
    assert result.mode is Mode.GENERATIVE


def test_security_requires_review(monkeypatch):
    mock_client(monkeypatch, fake_completion(
        provider_payload(category="SECURITY", priority="HIGH", requiresHumanReview=True)
    ))
    result = classify_generative("Alguien accedió a mi cuenta")
    assert result.category is Category.SECURITY
    assert result.requires_human_review is True


@pytest.mark.parametrize("payload", [
    provider_payload(category="OTHER"),
    provider_payload(mode="traditional"),
    provider_payload(category="SECURITY", requiresHumanReview=False),
    provider_payload(requiresHumanReview="false"),
    provider_payload(extra="invalido"),
    "texto no JSON",
    "[]",
    None,
])
def test_invalid_output(monkeypatch, payload):
    if payload is None:
        completion = SimpleNamespace(choices=[])
    else:
        completion = fake_completion(payload)
    mock_client(monkeypatch, completion)
    with pytest.raises(EngineExecutionError):
        classify_generative("Mensaje")


def test_provider_http_failure(monkeypatch):
    from groq import APIStatusError
    import httpx

    response = httpx.Response(
        403,
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )
    failure = APIStatusError("403", response=response, body=None)
    mock_client(monkeypatch, failure=failure)
    with pytest.raises(EngineExecutionError, match="No se pudo consultar"):
        classify_generative("Mensaje")


def test_provider_connection_failure(monkeypatch):
    from groq import APIConnectionError
    import httpx

    failure = APIConnectionError(
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    )
    mock_client(monkeypatch, failure=failure)
    with pytest.raises(EngineExecutionError, match="No se pudo consultar"):
        classify_generative("Mensaje")
