"""Reglas de detección de incidentes y revisión humana."""

import re
import unicodedata


def normalize_text(message: str) -> str:
    """Normaliza mayúsculas, acentos y espacios para comparar palabras."""
    text = unicodedata.normalize("NFKD", message.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip()


SECURITY_PATTERNS = (
    r"\b(acceso|ingreso|inicio de sesion|sesion) no autorizad[oa]s?\b",
    r"\b(entraron|ingresaron|accedieron) a mi (cuenta|perfil|sistema)\b",
    r"\b(robaron|robada|robado|hackearon|hackeada|hackeado|hackeo|hackeos)\b",
    r"\b(phishing|ransomware|malware|virus|brecha de seguridad|filtracion de datos)\b",
    r"\b(contrasena|password|credenciales|token|clave) (expuesta|expuesto|filtrada|filtrado|robada|robado|comprometida|comprometido)\b",
    r"\b(vulnerabilidad|inyeccion sql|sql injection|fuga de informacion)\b",
    r"\b(suplantacion de identidad|actividad sospechosa|intento de intrusion)\b",
)


def is_security_incident(message: str) -> bool:
    """Detecta señales explícitas de incidente, aun con instrucciones adversariales."""
    normalized = normalize_text(message)
    return any(re.search(pattern, normalized) for pattern in SECURITY_PATTERNS)
