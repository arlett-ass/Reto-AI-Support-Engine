"""Pruebas sin consumo de API del evaluador comparativo."""

import json
from pathlib import Path

from ai_support_engine.models import AnalyzeResponse
from scripts.compare_engines import evaluate, summarize


CASES_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "comparison_cases.json"


def test_fixture_has_required_cases():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    assert len(cases) >= 10
    assert len({case["id"] for case in cases}) == len(cases)
    assert sum(case["kind"] == "adversarial" for case in cases) >= 2
    assert any(case["kind"] == "ambiguo" for case in cases)
    assert {case["expected_category"] for case in cases} == {
        "ACCESS", "BUG", "FEATURE", "SECURITY"
    }


def test_comparison_uses_same_cases_and_counts_errors():
    cases = [
        {"id": "a", "kind": "normal", "message": "hola", "expected_category": "ACCESS"},
        {"id": "b", "kind": "normal", "message": "adios", "expected_category": "BUG"},
    ]
    def good(_message):
        return AnalyzeResponse(
            category="ACCESS", priority="MEDIUM", response="Ayuda",
            requiresHumanReview=False, mode="traditional"
        )
    def failing(_message):
        raise RuntimeError("no disponible")

    rows = evaluate(cases, {"traditional": good, "generative": failing})
    summary = summarize(rows, ("traditional", "generative"))
    assert summary["traditional"]["correct"] == 1
    assert summary["traditional"]["accuracy"] == 0.5
    assert summary["generative"]["correct"] == 0
    assert summary["generative"]["errors"] == 2
    assert rows[0]["engines"]["generative"]["error_type"] == "RuntimeError"
