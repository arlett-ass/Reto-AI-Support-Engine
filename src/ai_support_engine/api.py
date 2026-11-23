"""API HTTP del AI Support Engine."""

from collections.abc import Callable, Mapping
from typing import TypeAlias

from fastapi import FastAPI, HTTPException, status
from pydantic import ValidationError

from ai_support_engine.errors import EngineConfigurationError, EngineExecutionError
from ai_support_engine.models import AnalyzeRequest, AnalyzeResponse, Mode

ClassifierResult: TypeAlias = AnalyzeResponse | Mapping[str, object]
Classifier: TypeAlias = Callable[[str], ClassifierResult]


def _resolve_classifier(mode: Mode) -> Classifier:
    """Carga el motor real de forma diferida, cuando ya esté integrado."""
    try:
        if mode is Mode.TRADITIONAL:
            from ai_support_engine.traditional import classify_traditional

            return classify_traditional

        from ai_support_engine.generative import classify_generative

        return classify_generative
    except ImportError as exc:
        raise EngineConfigurationError("El motor solicitado no está disponible.") from exc


def _validate_result(result: ClassifierResult, requested_mode: Mode) -> AnalyzeResponse:
    """Valida el resultado del motor antes de serializarlo como respuesta HTTP."""
    try:
        response = AnalyzeResponse.model_validate(result)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El motor produjo una respuesta inválida.",
        ) from exc

    if response.mode is not requested_mode:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El motor devolvió un modo distinto al solicitado.",
        )

    return response


def create_app(
    *,
    traditional_classifier: Classifier | None = None,
    generative_classifier: Classifier | None = None,
) -> FastAPI:
    """Crea la API; los clasificadores inyectables permiten probar el despacho."""
    app = FastAPI(title="AI Support Engine", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/analyze", response_model=AnalyzeResponse)
    def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
        try:
            classifier = (
                traditional_classifier
                if request.mode is Mode.TRADITIONAL
                else generative_classifier
            )
            if classifier is None:
                classifier = _resolve_classifier(request.mode)
            result = classifier(request.message)
        except EngineConfigurationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El motor solicitado no está configurado.",
            ) from exc
        except EngineExecutionError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo completar el análisis solicitado.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="No se pudo completar el análisis solicitado.",
            ) from exc

        return _validate_result(result, request.mode)

    return app


app = create_app()
