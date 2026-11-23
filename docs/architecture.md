# Arquitectura implementada

## Componentes integrados

El proyecto contiene el paquete `src/ai_support_engine/`, el contrato JSON compartido en `models.py`, la API HTTP en `api.py` y los dos motores implementados en `traditional.py` y `generative.py`. Las pruebas del endpoint pueden inyectar clasificadores sin realizar llamadas externas.

## Flujo implementado

```text
cliente
  → POST /api/analyze (api.py)
  → AnalyzeRequest (models.py)
  → motor elegido por mode
      → classify_traditional(message) -> AnalyzeResponse
      → classify_generative(message) -> AnalyzeResponse
  → AnalyzeResponse validada por models.py
  → respuesta JSON
```

Los módulos `traditional.py`, `generative.py` y `security.py` ya están implementados. `api.py` permite inyectar clasificadores en las pruebas y, en ejecución normal, carga el motor real correspondiente al valor de `mode`. El motor tradicional aplica reglas sin proveedor externo y el generativo consulta Groq mediante su SDK y una API Key configurada localmente. Ambos motores utilizan estas firmas:

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

Pydantic valida el mismo esquema tanto al recibir la petición como al construir la respuesta. La API traduce las entradas inválidas a HTTP 422 y valida que el `mode` de la respuesta coincida con el solicitado.

La API responde HTTP 503 si el motor no está configurado y HTTP 502 si el motor falla o devuelve una respuesta inválida. Los detalles internos del proveedor no se devuelven al cliente.
