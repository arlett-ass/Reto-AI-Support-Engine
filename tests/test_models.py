import pytest
from pydantic import ValidationError

from ai_support_engine.models import AnalyzeRequest, AnalyzeResponse, Category, Mode, Priority


@pytest.mark.parametrize("mode", [Mode.TRADITIONAL, Mode.GENERATIVE])
def test_request_accepts_supported_modes(mode: Mode) -> None:
    request = AnalyzeRequest(message="No puedo iniciar sesión", mode=mode)

    assert request.message == "No puedo iniciar sesión"
    assert request.mode is mode


def test_request_strips_outer_whitespace() -> None:
    request = AnalyzeRequest(message="  No puedo iniciar sesión  ", mode="traditional")

    assert request.message == "No puedo iniciar sesión"


@pytest.mark.parametrize("message", ["", "   "])
def test_request_rejects_empty_message(message: str) -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message=message, mode="traditional")


def test_request_accepts_message_at_maximum_length() -> None:
    request = AnalyzeRequest(message="x" * 2000, mode="traditional")

    assert len(request.message) == 2000


def test_request_rejects_message_over_maximum_length() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message="x" * 2001, mode="traditional")


def test_request_rejects_unsupported_mode() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message="No puedo iniciar sesión", mode="automatic")


def test_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest(message="No puedo iniciar sesión", mode="traditional", user_id="123")


def test_response_serializes_the_teacher_contract() -> None:
    response = AnalyzeResponse.model_validate(
        {
            "category": "ACCESS",
            "priority": "MEDIUM",
            "response": "Utiliza la recuperación de contraseña.",
            "requiresHumanReview": False,
            "mode": "traditional",
        }
    )

    assert response.model_dump(mode="json", by_alias=True) == {
        "category": "ACCESS",
        "priority": "MEDIUM",
        "response": "Utiliza la recuperación de contraseña.",
        "requiresHumanReview": False,
        "mode": "traditional",
    }


@pytest.mark.parametrize("field,value", [("category", "UNKNOWN"), ("priority", "URGENT")])
def test_response_rejects_unknown_enum_values(field: str, value: str) -> None:
    payload = {
        "category": "BUG",
        "priority": "MEDIUM",
        "response": "Revisaremos el problema.",
        "requiresHumanReview": False,
        "mode": "traditional",
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)


def test_response_requires_a_real_boolean_for_human_review() -> None:
    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(
            {
                "category": "BUG",
                "priority": "MEDIUM",
                "response": "Revisaremos el problema.",
                "requiresHumanReview": "false",
                "mode": "traditional",
            }
        )


def test_security_response_requires_human_review() -> None:
    with pytest.raises(ValidationError, match="requieren revisión humana"):
        AnalyzeResponse(
            category=Category.SECURITY,
            priority=Priority.HIGH,
            response="El caso requiere revisión del equipo.",
            requires_human_review=False,
            mode=Mode.TRADITIONAL,
        )


def test_response_rejects_empty_response_and_extra_fields() -> None:
    payload = {
        "category": "BUG",
        "priority": "MEDIUM",
        "response": "   ",
        "requiresHumanReview": False,
        "mode": "traditional",
        "ticketId": 7,
    }

    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)
