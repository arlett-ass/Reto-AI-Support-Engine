"""Pruebas aisladas del motor: nunca requieren una clave real ni consumen API."""

import json
from urllib.error import HTTPError, URLError

import pytest

from ai_support_engine.errors import EngineConfigurationError, EngineExecutionError
from ai_support_engine.generative import classify_generative
from ai_support_engine.models import Category, Mode


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def provider_response(**overrides):
    result = {
        "category": "ACCESS",
        "priority": "MEDIUM",
        "response": "Prueba la recuperación de contraseña.",
        "requiresHumanReview": False,
        "mode": "generative",
    }
    result.update(overrides)
    return {"choices": [{"message": {"content": json.dumps(result)}}]}


def test_missing_key_is_configuration_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(EngineConfigurationError):
        classify_generative("No puedo iniciar sesión")


def test_real_http_request_shape_and_contract(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-token")
    monkeypatch.setenv("GROQ_MODEL", "test-model")

    def fake_urlopen(req, timeout):
        assert req.full_url.endswith("/chat/completions")
        assert timeout == 30
        assert req.get_header("Authorization") == "Bearer test-token"
        body = json.loads(req.data)
        assert body["model"] == "test-model"
        assert body["response_format"] == {"type": "json_object"}
        assert body["messages"][1]["content"] == "No puedo iniciar sesión"
        return FakeResponse(provider_response())

    monkeypatch.setattr("ai_support_engine.generative.request.urlopen", fake_urlopen)
    result = classify_generative("No puedo iniciar sesión")
    assert result.category is Category.ACCESS
    assert result.mode is Mode.GENERATIVE


def test_security_requires_human_review(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-token")
    monkeypatch.setattr(
        "ai_support_engine.generative.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(
            provider_response(category="SECURITY", priority="HIGH", requiresHumanReview=True)
        ),
    )
    result = classify_generative("Detecté un acceso no autorizado")
    assert result.category is Category.SECURITY
    assert result.requires_human_review is True


@pytest.mark.parametrize("invalid", [
    provider_response(category="OTHER"),
    provider_response(mode="traditional"),
    provider_response(category="SECURITY", requiresHumanReview=False),
    {"choices": []},
    {"choices": [{"message": {"content": "esto no es JSON"}}]},
    {"choices": [{"message": {"content": "[]"}}]},
])
def test_invalid_provider_outputs_fail_closed(monkeypatch, invalid):
    monkeypatch.setenv("GROQ_API_KEY", "test-token")
    monkeypatch.setattr(
        "ai_support_engine.generative.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(invalid),
    )
    with pytest.raises(EngineExecutionError):
        classify_generative("Mensaje")


@pytest.mark.parametrize("failure", [URLError("network"), TimeoutError("timeout"), HTTPError("url", 429, "rate limit", {}, None)])
def test_provider_failures_are_controlled(monkeypatch, failure):
    monkeypatch.setenv("GROQ_API_KEY", "test-token")

    def fail(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr("ai_support_engine.generative.request.urlopen", fail)
    with pytest.raises(EngineExecutionError):
        classify_generative("Mensaje")
