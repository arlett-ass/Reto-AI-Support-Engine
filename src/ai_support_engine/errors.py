"""Errores compartidos que la API traduce a respuestas HTTP seguras."""


class EngineConfigurationError(RuntimeError):
    """El motor solicitado no está configurado o disponible."""


class EngineExecutionError(RuntimeError):
    """El motor falló mientras procesaba una solicitud."""
