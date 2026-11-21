# Decisiones del proyecto

Este registro separa lo que el equipo ya comentó de las propuestas técnicas que todavía debe confirmar. El PR 0 sigue el plan compartido y deja visibles las decisiones pendientes para que puedan revisarse antes de integrar.

## Confirmado por el equipo

- El proyecto se implementará en Python.
- El contrato JSON seguirá el ejemplo del archivo del profesor.
- `development` será la rama de integración y `main` la rama estable.

## Propuestas del plan aplicadas en el PR 0

- El proyecto admite Python 3.11 y 3.12; el equipo debe acordar cuál usar como versión común.
- Se usa FastAPI para la futura API y Pydantic para validar el contrato compartido.
- El paquete vive en `src/ai_support_engine/` y las pruebas en `tests/`.

## Pendiente de confirmar

- La conversación del equipo menciona “Grop” para el motor generativo. Antes del PR generativo hay que confirmar si se refiere a Groq y acordar el identificador del modelo disponible.
- Confirmar que todo el equipo acepta FastAPI y Pydantic, como propone el plan.
- Acordar una única versión común de Python: 3.11 o 3.12.

No se guardan claves ni configuración privada en el repositorio.
