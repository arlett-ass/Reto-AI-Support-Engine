"""Ejecuta el mismo conjunto de casos contra ambos motores reales.

Uso: python scripts/compare_engines.py
Genera artifacts/comparison_results.json (no contiene credenciales).
"""

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from ai_support_engine.generative import classify_generative
from ai_support_engine.traditional import classify_traditional

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "fixtures" / "comparison_cases.json"
OUTPUT_PATH = ROOT / "artifacts" / "comparison_results.json"


def evaluate(cases, classifiers):
    """Evalúa todos los casos; registra fallos sin convertirlos en aciertos."""
    results = []
    for case in cases:
        row = {
            "id": case["id"],
            "kind": case["kind"],
            "expected_category": case["expected_category"],
            "engines": {},
        }
        for mode, classifier in classifiers.items():
            try:
                response = classifier(case["message"])
                output = response.model_dump(by_alias=True, mode="json")
                predicted = output["category"]
                row["engines"][mode] = {
                    "status": "ok",
                    "category": predicted,
                    "priority": output["priority"],
                    "requiresHumanReview": output["requiresHumanReview"],
                    "correct": predicted == case["expected_category"],
                    "security_review_ok": (
                        output["requiresHumanReview"] is True
                        if predicted == "SECURITY" else None
                    ),
                }
            except Exception as exc:
                # Solo registrar tipo de error; nunca detalles de red o tokens.
                row["engines"][mode] = {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "correct": False,
                }
        results.append(row)
    return results


def summarize(results, modes):
    summary = {}
    for mode in modes:
        total = len(results)
        correct = sum(row["engines"][mode]["correct"] for row in results)
        errors = sum(row["engines"][mode]["status"] == "error" for row in results)
        summary[mode] = {
            "total": total,
            "correct": correct,
            "errors": errors,
            "accuracy": round(correct / total, 4) if total else None,
        }
    return summary


def main():
    if not os.getenv("GROQ_API_KEY", "").strip():
        print("Falta GROQ_API_KEY. Configúrala en tu terminal.", file=sys.stderr)
        return 2

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if not cases:
        print("No hay casos para comparar.", file=sys.stderr)
        return 2

    classifiers = {
        "traditional": classify_traditional,
        "generative": classify_generative,
    }
    results = evaluate(cases, classifiers)
    summary = summarize(results, classifiers)
    artifact = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.system(),
            "groq_model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        },
        "methodology": "Mismos casos y etiquetas esperadas; fallos de proveedor cuentan como incorrectos.",
        "summary": summary,
        "results": results,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Comparación completada:", OUTPUT_PATH)
    for mode, metrics in summary.items():
        print(
            f"{mode}: {metrics['correct']}/{metrics['total']} "
            f"({metrics['accuracy']:.1%}), errores={metrics['errors']}"
        )
    return 1 if any(metrics["errors"] for metrics in summary.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
