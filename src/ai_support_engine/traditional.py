"""Motor tradicional determinista basado en reglas y sin servicios externos."""

import re

from ai_support_engine.models import AnalyzeResponse, Category, Mode, Priority
from ai_support_engine.security import is_security_incident, normalize_text


RULES = {
    Category.ACCESS: (
        r"\b(iniciar sesion|inicio de sesion|login|acceder|acceso|entrar|ingresar)\b",
        r"\b(contrasena|password|usuario|credenciales|autenticacion|bloqueada|bloqueado)\b",
    ),
    Category.BUG: (
        r"\b(error|errores|bug|falla|fallo|falla tecnica|no funciona|dejo de funcionar)\b",
        r"\b(se cierra|se congela|crash|pantalla blanca|pantalla negra|no carga)\b",
    ),
    Category.FEATURE: (
        r"\b(nueva funcion|nueva funcionalidad|agregar|anadir|incorporar|implementar)\b",
        r"\b(mejora|mejorar|opcion nueva|solicito|me gustaria|seria util)\b",
    ),
}

RESPONSES = {
    Category.ACCESS: "Verifica tus datos de acceso y utiliza la recuperación de contraseña si es necesario.",
    Category.BUG: "Indica los pasos para reproducir la falla y el mensaje de error para que soporte pueda revisarlo.",
    Category.FEATURE: "Describe la función que necesitas y cómo te ayudaría para evaluar la solicitud.",
    Category.SECURITY: "Protege tu cuenta, evita compartir credenciales y reporta el incidente al equipo de seguridad.",
}


def _matches(text: str, patterns: tuple[str, ...]) -> int:
    return sum(bool(re.search(pattern, text)) for pattern in patterns)


def classify_traditional(message: str) -> AnalyzeResponse:
    """Clasifica con reglas explícitas; incidentes de seguridad tienen precedencia."""
    if is_security_incident(message):
        category = Category.SECURITY
        priority = Priority.CRITICAL
        review = True
    else:
        text = normalize_text(message)
        scores = {category: _matches(text, patterns) for category, patterns in RULES.items()}
        # Orden determinista para empates: BUG, ACCESS, FEATURE.
        order = (Category.BUG, Category.ACCESS, Category.FEATURE)
        category = max(order, key=lambda item: scores[item])
        if scores[category] == 0:
            category = Category.BUG
            priority = Priority.MEDIUM
            review = True  # Mensajes ambiguos no se cierran automáticamente.
        else:
            priority = Priority.MEDIUM if category is not Category.FEATURE else Priority.LOW
            review = False

    return AnalyzeResponse(
        category=category,
        priority=priority,
        response=RESPONSES[category],
        requiresHumanReview=review,
        mode=Mode.TRADITIONAL,
    )
