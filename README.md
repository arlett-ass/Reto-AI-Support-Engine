# Reto AI Support Engine

Prototipo de clasificación de solicitudes de soporte con un motor tradicional basado en reglas y otro generativo.

## Estado

El PR 0 prepara el contrato compartido y la estructura del paquete. La API y los dos motores se implementarán en PR posteriores. El trabajo se integra en `development`; `main` conserva la versión estable.

## Integrantes

- Angelica Arlett Santiago Serrano
- Nicolás David Juarez Mendoza
- Victor Manuel Jimenez Suarez

## Requisitos

- Python 3.12.
- Git.

## Instalación para desarrollo

Desde la raíz del repositorio, crea y activa un entorno virtual. En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Después instala el paquete y las dependencias de desarrollo:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Ejecuta las pruebas del contrato con:

```bash
python -m pytest -v
```

## Contrato compartido

`POST /api/analyze` aceptará un JSON con `message` y `mode`. `mode` será `traditional` o `generative`. La respuesta tendrá `category`, `priority`, `response`, `requiresHumanReview` y `mode`; los valores de categoría y prioridad están limitados a las enumeraciones del reto. El contrato vive en `src/ai_support_engine/models.py` y se valida con Pydantic.

En esta fase todavía no hay una API ejecutable ni motores que procesen solicitudes.
