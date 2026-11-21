# Arquitectura inicial

## Alcance del PR 0

El PR 0 establece un paquete Python en `src/ai_support_engine/`, un contrato JSON único en `models.py` y pruebas del contrato. Todavía no implementa la API ni los motores.

## Flujo previsto

```text
cliente
  → POST /api/analyze (api.py)
  → AnalyzeRequest (models.py)
  → motor elegido por mode
      → classify_traditional(message) -> AnalyzeResponse
      → classify_generative(message) -> AnalyzeResponse
  → validación de AnalyzeResponse
  → respuesta JSON
```

Los módulos `api.py`, `traditional.py`, `generative.py` y `security.py` se agregarán en PR posteriores. Los motores compartirán estas firmas:

```python
def classify_traditional(message: str) -> AnalyzeResponse: ...
def classify_generative(message: str) -> AnalyzeResponse: ...
```

## Contrato

La petición tiene exactamente estos campos:

```json
{"message": "No puedo iniciar sesión", "mode": "traditional"}
```

La respuesta tiene exactamente cinco campos:

```json
{
  "category": "ACCESS",
  "priority": "MEDIUM",
  "response": "Utiliza la recuperación de contraseña.",
  "requiresHumanReview": false,
  "mode": "traditional"
}
```

`message` debe contener entre 1 y 2000 caracteres después de quitar espacios exteriores. `mode` acepta `traditional` o `generative`. `category` acepta `ACCESS`, `BUG`, `FEATURE` o `SECURITY`; `priority` acepta `LOW`, `MEDIUM`, `HIGH` o `CRITICAL`. No se permiten campos adicionales. Una respuesta `SECURITY` debe requerir revisión humana.

Pydantic valida el mismo esquema tanto al recibir la petición como al construir la respuesta. La API traducirá las entradas inválidas a HTTP 422 y validará que el `mode` de la respuesta coincida con el solicitado.
