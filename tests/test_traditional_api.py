"""Integración real del motor tradicional con el endpoint HTTP."""

from fastapi.testclient import TestClient

from ai_support_engine.api import app


client = TestClient(app)


def test_real_traditional_endpoint():
    response = client.post("/api/analyze", json={
        "message": "No puedo iniciar sesión",
        "mode": "traditional",
    })
    assert response.status_code == 200
    assert response.json() == {
        "category": "ACCESS",
        "priority": "MEDIUM",
        "response": "Verifica tus datos de acceso y utiliza la recuperación de contraseña si es necesario.",
        "requiresHumanReview": False,
        "mode": "traditional",
    }


def test_real_security_endpoint():
    response = client.post("/api/analyze", json={
        "message": "Detecté un acceso no autorizado",
        "mode": "traditional",
    })
    assert response.status_code == 200
    assert response.json()["category"] == "SECURITY"
    assert response.json()["requiresHumanReview"] is True
