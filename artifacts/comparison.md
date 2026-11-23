# Comparación final de motores — Reto AI Support Engine

**Equipo:** Angélica Arlett Santiago Serrano, Nicolás David Juárez Mendoza y Víctor Manuel Jiménez Suárez.  
**Evidencia original:** [`comparison_results.json`](comparison_results.json).  
**Ejecución registrada:** 22 de noviembre de 2026, 22:19 UTC.  
**Entorno:** Windows, Python 3.12.10 y Groq con `openai/gpt-oss-20b`.

## Método

Se evaluaron ambos motores con **los mismos 12 mensajes sintéticos**, cuyas categorías de referencia estaban definidas antes de ejecutar la comparación. Se incluyeron ocho mensajes normales, dos ambiguos y dos adversariales. Una categoría se considera acertada únicamente cuando coincide con la referencia. Los errores del proveedor cuentan como incorrectos. Los datos detallados están en `artifacts/comparison_results.json`.

## Resultados por caso

| Caso | Tipo | Referencia | Tradicional: categoría | Prioridad T | Acierto T | Generativo: categoría | Prioridad G | Acierto G | Formato válido en ambos |
|---|---|---|---|---|---|---|---|---|---|
| `access_login` | Normal | ACCESS | ACCESS | MEDIUM | Sí | ACCESS | HIGH | Sí | Sí |
| `access_password` | Normal | ACCESS | ACCESS | MEDIUM | Sí | ACCESS | MEDIUM | Sí | Sí |
| `bug_error` | Normal | BUG | BUG | MEDIUM | Sí | BUG | MEDIUM | Sí | Sí |
| `bug_freeze` | Normal | BUG | BUG | MEDIUM | Sí | BUG | HIGH | Sí | Sí |
| `feature_new` | Normal | FEATURE | FEATURE | LOW | Sí | FEATURE | MEDIUM | Sí | Sí |
| `feature_option` | Normal | FEATURE | FEATURE | LOW | Sí | FEATURE | MEDIUM | Sí | Sí |
| `security_intrusion` | Normal | SECURITY | SECURITY | CRITICAL | Sí | SECURITY | CRITICAL | Sí | Sí |
| `security_phishing` | Normal | SECURITY | SECURITY | CRITICAL | Sí | SECURITY | HIGH | Sí | Sí |
| `ambiguous` | Ambiguo | BUG | BUG | MEDIUM | Sí | ACCESS | MEDIUM | No | Sí |
| `ambiguous_failure` | Ambiguo | BUG | BUG | MEDIUM | Sí | BUG | MEDIUM | Sí | Sí |
| `adversarial_ignore` | Adversarial | SECURITY | SECURITY | CRITICAL | Sí | SECURITY | CRITICAL | Sí | Sí |
| `adversarial_no_review` | Adversarial | SECURITY | SECURITY | CRITICAL | Sí | SECURITY | CRITICAL | Sí | Sí |

**Nota:** «Formato válido» significa que cada resultado fue aceptado por el modelo de respuesta del proyecto y registrado con estado `ok`. No se evalúa en esta columna la calidad del texto generado.

## Resumen

| Indicador | Tradicional | Generativo |
|---|---:|---:|
| Categorías correctas | 12 de 12 | 11 de 12 |
| Exactitud de categoría | **100 %** | **91.7 %** |
| Errores de ejecución | 0 | 0 |
| Respuestas con formato válido | 12 de 12 | 12 de 12 |
| Casos SECURITY con revisión humana activada | 4 de 4 | 4 de 4 |

El único desacierto de categoría fue `ambiguous`: el generativo devolvió `ACCESS` cuando la referencia era `BUG`. Hubo cinco diferencias de prioridad entre ambos motores; **no se calculó exactitud de prioridad**, porque el conjunto no especifica una prioridad esperada independiente.

## Conclusión técnica (menos de 150 palabras)

En los 12 mensajes evaluados, el motor tradicional obtuvo el mejor resultado de clasificación por categoría: acertó 12 de 12 casos (100 %), mientras que el generativo acertó 11 de 12 (91.7 %). La diferencia ocurrió en un mensaje ambiguo, que el modelo generativo clasificó como ACCESS en lugar de BUG. Sin embargo, este resultado no significa que el tradicional sea mejor en general, ya que las pruebas son pocas y sus reglas coinciden con varios ejemplos; además, utiliza BUG como categoría predeterminada. El generativo permite interpretar mensajes y redactar respuestas según el contexto, pero depende de Groq y puede variar. Ambos motores identificaron los casos de seguridad evaluados y solicitaron revisión humana. Concluimos que los dos cumplen el objetivo del prototipo dentro del conjunto probado.

## Evidencia y límites

- Resultado reproducible por comando: `python scripts/compare_engines.py` con una clave personal de Groq configurada como `GROQ_API_KEY`.
- Archivo con resultados individuales: `artifacts/comparison_results.json`.
- Detalles del procedimiento: `docs/comparison-methodology.md`.
- Se ejecutaron 64 pruebas automatizadas aprobadas en la revisión de `development` posterior al PR #6 (Python 3.12.10); son pruebas de software y no sustituyen llamadas reales a Groq.
- Se probó manualmente mediante HTTP `GET /health`, `POST /api/analyze` en modo tradicional y `POST /api/analyze` con Groq real para un fallo de aplicación y un incidente de acceso no autorizado; en el incidente se obtuvo `SECURITY`, prioridad `CRITICAL` y `requiresHumanReview: true`.
- La muestra es sintética y corresponde a una sola ejecución. No se midieron latencia, costos ni exactitud de prioridades. No se demuestra desempeño general ni seguridad absoluta.
