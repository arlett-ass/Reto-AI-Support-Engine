"""Contrato JSON compartido por la API y los motores de clasificación."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator


class Category(str, Enum):
    """Categorías permitidas para una solicitud de soporte."""

    ACCESS = "ACCESS"
    BUG = "BUG"
    FEATURE = "FEATURE"
    SECURITY = "SECURITY"


class Priority(str, Enum):
    """Niveles de prioridad permitidos para una solicitud."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Mode(str, Enum):
    """Motor que debe atender la solicitud."""

    TRADITIONAL = "traditional"
    GENERATIVE = "generative"


class ContractModel(BaseModel):
    """Configuración común para rechazar campos desconocidos y normalizar texto."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class AnalyzeRequest(ContractModel):
    """Entrada de `POST /api/analyze`."""

    message: str = Field(min_length=1, max_length=2000)
    mode: Mode


class AnalyzeResponse(ContractModel):
    """Respuesta común de ambos motores."""

    category: Category
    priority: Priority
    response: str = Field(min_length=1)
    requires_human_review: StrictBool = Field(alias="requiresHumanReview")
    mode: Mode

    @model_validator(mode="after")
    def security_requires_human_review(self) -> "AnalyzeResponse":
        """No permitir que una categoría de seguridad se cierre automáticamente."""
        if self.category is Category.SECURITY and not self.requires_human_review:
            raise ValueError("Las solicitudes SECURITY requieren revisión humana")
        return self


__all__ = [
    "AnalyzeRequest",
    "AnalyzeResponse",
    "Category",
    "Mode",
    "Priority",
]
