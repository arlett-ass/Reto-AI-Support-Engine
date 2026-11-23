# PR 5 — Comparación reproducible de motores

## Objetivo
Comparar la clasificación de solicitudes del motor tradicional y del generativo de Groq con **las mismas entradas** y etiquetas de referencia.

## Casos y método
`fixtures/comparison_cases.json` contiene 12 casos sintéticos: acceso, fallas, funciones, incidentes de seguridad, mensajes ambiguos y dos intentos adversariales. Las etiquetas `expected_category` se definieron como referencia antes de ejecutar los motores; no son predicciones del proveedor.

Se ejecutó `python scripts/compare_engines.py` con Python 3.12.10 en Windows y modelo `openai/gpt-oss-20b`. La ejecución está registrada en `artifacts/comparison_results.json` con fecha UTC `2026-11-22T22:19:00.429056+00:00`. Las pruebas automatizadas locales reportaron **64 aprobadas**.

## Resultados observados (una ejecución)
| Motor | Correctos / total | Exactitud de categoría | Errores de proveedor |
| --- | ---: | ---: | ---: |
| Tradicional | 12/12 | 100 % | 0 |
| Generativo | 11/12 | 91.7 % | 0 |

El único desacuerdo de categoría fue el caso `ambiguous`: el esperado era `BUG`, el tradicional respondió `BUG` y el generativo respondió `ACCESS`. El mensaje no describe una falla concreta, por lo que su etiqueta de referencia es discutible.

En cuatro casos (`access_login`, `bug_freeze`, `feature_new`, `feature_option`) el generativo asignó una prioridad distinta a la del tradicional; en `security_phishing` también difirió (HIGH frente a CRITICAL). **Son cinco diferencias de prioridad** en total. No se calcularon aciertos de prioridad porque el conjunto solo define categorías esperadas. Ambos motores marcaron revisión humana en los cuatro casos clasificados como SECURITY (dos normales y dos adversariales).

## Limitaciones
- Exactitud = clasificaciones de categoría correctas / 12; una llamada fallida cuenta como incorrecta y se reporta aparte.
- El conjunto es pequeño, sintético y no representa producción. El 100 % del tradicional no demuestra superioridad general.
- El tradicional asigna `BUG` por defecto cuando no reconoce palabras clave; los dos casos ambiguos tienen `BUG` como referencia. Esto favorece al tradicional en esa parte del conjunto.
- Las etiquetas de casos ambiguos son interpretables; se necesita evaluación humana independiente para conclusiones más fuertes.
- El modelo generativo puede variar entre ejecuciones; este resultado representa **una sola corrida**.
- No se midieron tiempos, costos, calidad de respuestas ni precisión de prioridades; no se deben atribuir mejoras en esas dimensiones.
- Las pruebas de instrucciones adversariales son casos puntuales, no una garantía general de seguridad.

## Reproducción
1. Activar Python 3.12 e instalar `python -m pip install -e .` y `python -m pip install -r requirements-dev.txt`.
2. Ejecutar `python -m pytest -v`.
3. Configurar `GROQ_API_KEY` solo localmente y opcionalmente `GROQ_MODEL=openai/gpt-oss-20b`.
4. Ejecutar `python scripts/compare_engines.py`.
5. Inspeccionar `artifacts/comparison_results.json` antes de subirlo: no incluir secretos ni datos reales sensibles.

## Estado de la documentación y evidencias

El README definitivo fue actualizado e integrado a development mediante el PR #6.

La comparación final se presenta en
[comparison.md](../artifacts/comparison.md),
incluyendo la tabla de 12 casos, los resultados de ambos motores
y una conclusión técnica de menos de 150 palabras.

Los resultados originales se conservan en
[comparison_results.json](../artifacts/comparison_results.json).

También se verificó el funcionamiento de la API mediante
solicitudes HTTP reales a los motores tradicional y generativo.
El entorno local superó 64 pruebas automatizadas.

Antes de la entrega se debe validar nuevamente development,
integrar los cambios finales a main mediante un Pull Request
y comprobar el funcionamiento de la versión entregada.