# PR 5 — Comparación reproducible de motores

## Objetivo
Comparar la clasificación de solicitudes del motor tradicional y del generativo de Groq con **las mismas entradas** y etiquetas de referencia.

## Casos
`fixtures/comparison_cases.json` contiene 12 casos sintéticos: acceso, fallas, funciones, incidentes de seguridad, mensajes ambiguos y dos intentos adversariales. Las etiquetas `expected_category` son una referencia definida antes de ejecutar los motores; no son predicciones del proveedor. Los mensajes ambiguos tienen una etiqueta operativa para calcular la métrica, pero admiten interpretación distinta.

## Ejecución
1. Activar el entorno Python 3.12 y ejecutar `python -m pip install -e .`.
2. Ejecutar `python -m pytest -v`.
3. Configurar `GROQ_API_KEY` de forma local y `GROQ_MODEL=openai/gpt-oss-20b`.
4. Ejecutar `python scripts/compare_engines.py`.
5. Revisar `artifacts/comparison_results.json` antes de compartirlo como evidencia. **No subir claves** ni salidas con información privada.

## Métrica y límites
Exactitud = clasificaciones correctas / total de casos. Una llamada fallida cuenta como incorrecta y se reporta por separado. Se informa exactitud por motor, sin afirmar superioridad general por una muestra pequeña. El modelo generativo puede variar entre ejecuciones; los resultados dependen del modelo, fecha y disponibilidad de Groq. El conjunto es sintético y no representa producción.

## Evidencia pendiente
Los porcentajes y observaciones deben completarse **después de ejecutar ambos motores realmente**. No hay resultados predeterminados ni cifras inventadas. El PR se mantiene en borrador hasta validar las pruebas y la comparación real.
