import pytest
from fastapi.testclient import TestClient

import ai_support_engine.api as api_module
from ai_support_engine.api import create_app
from ai_support_engine.errors import EngineConfigurationError, EngineExecutionError
from ai_support_engine.models import Mode


def response_for(mode: Mode) -> dict[str, object]:
    return {
        "category": "ACCESS",
        "priority": "MEDIUM",
        "response": "Utiliza la recuperación de contraseña.",
        "requiresHumanReview": False,
        "mode": mode.value,
    }


@pytest.mark.parametrize(
    ("mode", "expected_mode"),
    [
        (Mode.TRADITIONAL, Mode.TRADITIONAL),
        (Mode.GENERATIVE, Mode.GENERATIVE),
    ],
)
def test_analyze_dispatches_and_returns_the_shared_contract(
    mode: Mode, expected_mode: Mode
) -> None:
    calls: list[tuple[str, str]] = []

    def traditional(message: str) -> dict[str, object]:
        calls.append(("traditional", message))
        return response_for(Mode.TRADITIONAL)

    def generative(message: str) -> dict[str, object]:
        calls.append(("generative", message))
        return response_for(Mode.GENERATIVE)

    client = TestClient(
        create_app(
            traditional_classifier=traditional,
            generative_classifier=generative,
        )
    )

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": mode.value},
    )

    assert result.status_code == 200
    assert result.json() == response_for(expected_mode)
    assert calls == [(mode.value, "No puedo iniciar sesión")]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": "   ", "mode": "traditional"},
        {"message": "x" * 2001, "mode": "traditional"},
        {"message": "Necesito ayuda", "mode": "automatic"},
        {"message": "Necesito ayuda", "mode": "traditional", "extra": True},
    ],
)
def test_analyze_returns_422_for_invalid_input(payload: dict[str, object]) -> None:
    client = TestClient(create_app(traditional_classifier=lambda _: response_for(Mode.TRADITIONAL)))

    result = client.post("/api/analyze", json=payload)

    assert result.status_code == 422


def test_analyze_returns_503_when_engine_configuration_is_missing() -> None:
    def unconfigured(_: str) -> dict[str, object]:
        raise EngineConfigurationError("GROQ_API_KEY is not set")

    client = TestClient(create_app(generative_classifier=unconfigured))

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "generative"},
    )

    assert result.status_code == 503
    assert result.json() == {"detail": "El motor solicitado no está configurado."}
    assert "GROQ_API_KEY" not in result.text


def test_analyze_returns_503_when_default_engine_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(_: Mode) -> object:
        raise EngineConfigurationError("engine module is not integrated")

    monkeypatch.setattr(api_module, "_resolve_classifier", unavailable)
    client = TestClient(create_app())

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "traditional"},
    )

    assert result.status_code == 503
    assert result.json() == {"detail": "El motor solicitado no está configurado."}


def test_analyze_returns_502_for_engine_provider_failure() -> None:
    def provider_failure(_: str) -> dict[str, object]:
        raise EngineExecutionError("Provider returned 429")

    client = TestClient(create_app(generative_classifier=provider_failure))

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "generative"},
    )

    assert result.status_code == 502
    assert result.json() == {"detail": "No se pudo completar el análisis solicitado."}
    assert "429" not in result.text


def test_analyze_hides_unexpected_engine_errors() -> None:
    def broken_engine(_: str) -> dict[str, object]:
        raise RuntimeError("private provider details")

    client = TestClient(create_app(traditional_classifier=broken_engine))

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "traditional"},
    )

    assert result.status_code == 502
    assert "private provider details" not in result.text


def test_analyze_returns_502_for_invalid_engine_output() -> None:
    invalid_output = response_for(Mode.TRADITIONAL)
    invalid_output["category"] = "UNKNOWN"
    client = TestClient(create_app(traditional_classifier=lambda _: invalid_output))

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "traditional"},
    )

    assert result.status_code == 502
    assert result.json() == {"detail": "El motor produjo una respuesta inválida."}


def test_analyze_returns_502_if_engine_returns_the_wrong_mode() -> None:
    client = TestClient(
        create_app(traditional_classifier=lambda _: response_for(Mode.GENERATIVE))
    )

    result = client.post(
        "/api/analyze",
        json={"message": "No puedo iniciar sesión", "mode": "traditional"},
    )

    assert result.status_code == 502
    assert result.json() == {"detail": "El motor devolvió un modo distinto al solicitado."}


def test_health_returns_ok() -> None:
    client = TestClient(create_app())

    result = client.get("/health")

    assert result.status_code == 200
    assert result.json() == {"status": "ok"}
