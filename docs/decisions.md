# Decisiones del proyecto

## Confirmadas por el equipo

- Usar Python 3.12 como versión común.
- Usar FastAPI para la API y Pydantic para validar el contrato compartido.
- Seguir el ejemplo de JSON del archivo del profesor.
- Integrar el trabajo en `development` y mantener `main` como rama estable.
- Mantener el paquete en `src/ai_support_engine/` y las pruebas en `tests/`.

## Motor generativo confirmado

- Se utiliza Groq mediante su SDK de Python, con `openai/gpt-oss-20b` como modelo predeterminado en `generative.py`.
- La clave se configura mediante la variable de entorno `GROQ_API_KEY`. No se guardan claves ni configuración privada en el repositorio.
