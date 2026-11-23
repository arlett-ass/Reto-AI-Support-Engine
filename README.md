# Reto AI Support Engine

**Prototipo de clasificación de solicitudes de soporte técnico mediante dos motores: uno tradicional y otro generativo.**

## 1. Descripción y objetivo

Reto AI Support Engine recibe mensajes de soporte y los clasifica para ayudar a identificar su tipo, prioridad y necesidad de revisión humana. El usuario puede elegir entre dos formas de análisis a través de una API desarrollada con FastAPI:

- **Motor tradicional:** utiliza expresiones y palabras clave. No necesita conexión con un proveedor de inteligencia artificial.
- **Motor generativo:** envía el mensaje a la API de Groq y utiliza el modelo `openai/gpt-oss-20b` (modelo predeterminado en el código). Necesita una clave de API y conexión a Internet.

Ambos motores devuelven el mismo formato JSON. Este proyecto es un prototipo académico: sus clasificaciones son orientativas y no sustituyen la revisión humana, especialmente en incidentes de seguridad.

## 2. Integrantes

- Angélica Arlett Santiago Serrano
- Nicolás David Juárez Mendoza
- Víctor Manuel Jiménez Suárez

## 3. Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
| --- | --- |
| Python 3.12 | Lenguaje de programación (el proyecto requiere `>=3.12,<3.13`) |
| FastAPI | API HTTP para recibir y responder solicitudes |
| Pydantic | Validación del formato de entrada y salida |
| Groq (SDK de Python) | Consulta del motor generativo |
| Uvicorn | Servidor para ejecutar FastAPI |
| pytest | Pruebas automatizadas |
| Git y GitHub | Control de versiones, ramas y pull requests |

Las versiones y rangos de dependencias están declarados en `pyproject.toml` y `requirements-dev.txt`.

## 4. Organización del repositorio

```text
Reto-AI-Support-Engine/
├── src/ai_support_engine/
│   ├── api.py                  # Endpoints HTTP y selección de motor
│   ├── models.py               # Contrato de entrada y salida
│   ├── traditional.py          # Clasificación por reglas
│   ├── generative.py           # Clasificación con Groq
│   ├── security.py             # Detección de indicios de seguridad
│   └── errors.py               # Errores definidos para los motores
├── tests/                      # Pruebas automatizadas
├── fixtures/
│   └── comparison_cases.json   # 12 mensajes sintéticos de comparación
├── scripts/
│   └── compare_engines.py      # Comparación de ambos motores
├── docs/
│   └── comparison-methodology.md
├── artifacts/
│   └── comparison_results.json # Evidencia de una ejecución real
├── .env.example                # Ejemplo de configuración (sin claves)
├── pyproject.toml              # Metadatos y dependencias principales
├── requirements-dev.txt        # Dependencias para pruebas
└── README.md
```

## 5. Instalación desde cero

### 5.1. Requisitos

- Python **3.12** (Python 3.13 no cumple la restricción actual del proyecto).
- Git.
- Conexión a Internet para instalar las dependencias y, si se utiliza el motor generativo, consultar Groq.

### 5.2. Descargar el repositorio

```bash
git clone https://github.com/arlett-ass/Reto-AI-Support-Engine.git
cd Reto-AI-Support-Engine
```

**Nota sobre las ramas:** durante el desarrollo, los PR se fusionan primero a `development`. Una vez que el proyecto esté validado e integrado para entrega, `main` debe contener la versión final. Para revisar la versión de desarrollo antes de esa integración, ejecutar `git switch development` y `git pull --ff-only origin development`.

### 5.3. Preparar Python en Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

### 5.4. Preparar Python en Linux o macOS

Usar un intérprete **Python 3.12** instalado en el sistema:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## 6. Configuración del motor generativo

Para utilizar el modo `generative`, se necesita una clave válida de Groq. El evaluador puede crear una clave propia desde [GroqCloud API Keys](https://console.groq.com/keys); no necesita la clave del equipo. **No la agregues al código, al README, a los commits ni a capturas de pantalla.**

En Windows PowerShell, dentro de la terminal desde la cual iniciarás el servidor:

```powershell
$secureKey = Read-Host "Introduce tu GROQ_API_KEY" -AsSecureString
$env:GROQ_API_KEY = [System.Net.NetworkCredential]::new("", $secureKey).Password
Remove-Variable secureKey
$env:GROQ_MODEL = "openai/gpt-oss-20b"
```

En Linux o macOS:

```bash
read -rsp "Introduce tu GROQ_API_KEY: " GROQ_API_KEY
printf '\n'
export GROQ_API_KEY
export GROQ_MODEL="openai/gpt-oss-20b"
```

`GROQ_MODEL` es opcional: si no se configura, el código utiliza `openai/gpt-oss-20b` de manera predeterminada. Las variables definidas así son temporales: al abrir otra terminal hay que configurarlas de nuevo antes de iniciar Uvicorn. El archivo `.env.example` muestra los nombres de las variables, pero **el programa no carga automáticamente archivos `.env`**: debes definir las variables en el entorno de ejecución. Las credenciales reales nunca deben subirse al repositorio.

El modo `traditional` funciona sin configurar Groq. También pueden ejecutarse las pruebas automatizadas sin clave real; la validación de conexión con Groq sí exige una clave válida.

## 7. Iniciar la API

Con el entorno virtual activado, desde la raíz del repositorio:

```bash
python -m uvicorn ai_support_engine.api:app --host 127.0.0.1 --port 8000
```

La aplicación estará disponible de manera local en `http://127.0.0.1:8000`. En el navegador puedes abrir:

- Documentación interactiva (Swagger): `http://127.0.0.1:8000/docs`
- Esquema OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Comprobación de salud: `http://127.0.0.1:8000/health`

Para detener el servidor, presiona **Ctrl+C** en su terminal.

## 8. Endpoints de la API

| Método | Ruta | Función |
| --- | --- | --- |
| `GET` | `/health` | Comprueba que la API responde; devuelve `{"status":"ok"}` |
| `POST` | `/api/analyze` | Analiza un mensaje con el motor seleccionado |

### 8.1. Cuerpo de la solicitud

```json
{
  "message": "No puedo iniciar sesión",
  "mode": "traditional"
}
```

- `message`: texto obligatorio, de 1 a 2000 caracteres después de eliminar espacios exteriores.
- `mode`: `traditional` o `generative`.

### 8.2. Ejemplo probado: motor tradicional

En otra terminal PowerShell, con el servidor en ejecución:

```powershell
$body = @{
    message = "No puedo iniciar sesión"
    mode = "traditional"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/analyze" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $body
```

Respuesta observada en una prueba manual local:

```json
{
  "category": "ACCESS",
  "priority": "MEDIUM",
  "response": "Verifica tus datos de acceso y utiliza la recuperación de contraseña si es necesario.",
  "requiresHumanReview": false,
  "mode": "traditional"
}
```

### 8.3. Ejemplo probado: motor generativo con Groq real

Con `GROQ_API_KEY` configurada y el servidor iniciado **desde la misma terminal** que tiene las variables de entorno:

```powershell
$body = @{
    message = "La aplicación se congela al guardar un reporte"
    mode = "generative"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/analyze" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $body
```

Respuesta observada en una prueba manual real con Groq (puede variar en otra ejecución):

```json
{
  "category": "BUG",
  "priority": "HIGH",
  "response": "Lo sentimos por el inconveniente. Intente cerrar y volver a abrir la aplicación, o reinstalarla. Si el problema persiste, envíe los logs de la sesión para que podamos investigarlo.",
  "requiresHumanReview": false,
  "mode": "generative"
}
```

### 8.4. Ejemplo probado: incidente de seguridad con Groq real

Solicitud de ejemplo:

```json
{
  "message": "Detecté un acceso no autorizado a mi cuenta",
  "mode": "generative"
}
```

Respuesta observada en la prueba manual:

```json
{
  "category": "SECURITY",
  "priority": "CRITICAL",
  "response": "Lamentamos el inconveniente. Por favor, cambia tu contraseña inmediatamente y revisa la actividad reciente. Si sospechas actividad maliciosa, contacta a nuestro equipo de soporte de inmediato.",
  "requiresHumanReview": true,
  "mode": "generative"
}
```

El motor generativo devuelve el mismo contrato que el tradicional, pero sus decisiones y redacción pueden variar entre ejecuciones.

## 9. Categorías, prioridades y revisión humana

Las categorías permitidas son:

| Categoría | Significado |
| --- | --- |
| `ACCESS` | Dificultades de acceso o autenticación |
| `BUG` | Errores o fallas de una aplicación |
| `FEATURE` | Solicitudes de nuevas funciones o mejoras |
| `SECURITY` | Indicios de vulnerabilidades o incidentes de seguridad |

Las prioridades disponibles son `LOW`, `MEDIUM`, `HIGH` y `CRITICAL`. No todos los casos llevan la misma prioridad: el motor tradicional aplica reglas definidas y el generativo determina la suya mediante el modelo.

El campo `requiresHumanReview` indica si la solicitud requiere revisión de una persona. El contrato **obliga a que toda respuesta de categoría `SECURITY` tenga `requiresHumanReview: true`**. El motor tradicional también solicita revisión humana cuando el mensaje es ambiguo y no identifica una categoría mediante las reglas.

## 10. Validaciones y respuestas HTTP

| Código HTTP | Cuándo ocurre |
| --- | --- |
| `200` | El análisis se completó correctamente |
| `422` | La solicitud tiene datos inválidos: mensaje vacío, demasiado largo, modo desconocido o campos adicionales |
| `503` | El motor solicitado no está configurado o no puede cargarse; por ejemplo, falta `GROQ_API_KEY` en modo generativo |
| `502` | El proveedor falla, produce una respuesta inválida o el motor no puede completar el análisis |

La API devuelve mensajes de error controlados para evitar exponer detalles internos del proveedor.

## 11. Pruebas y comparación de motores

Para ejecutar las pruebas automatizadas:

```bash
python -m pytest -v
```

En la revisión local de `development` y, posteriormente, durante los cambios del README se obtuvieron **64 pruebas aprobadas** con Python 3.12.10. Las pruebas cubren el contrato, el despacho HTTP, validaciones, errores, casos del motor tradicional, lógica del generativo con simulaciones y el comparador. **Estas pruebas no equivalen a una llamada real a Groq**.

Para reproducir la comparación con Groq real, primero configura `GROQ_API_KEY`, luego ejecuta:

```bash
python scripts/compare_engines.py
```

El script utiliza los 12 casos sintéticos de `fixtures/comparison_cases.json` y genera `artifacts/comparison_results.json`. Una falla del proveedor se registra como error y cuenta como clasificación incorrecta en la exactitud.

### Resultados medidos en una ejecución

| Motor | Categorías acertadas | Exactitud sobre 12 casos | Errores de ejecución |
| --- | ---: | ---: | ---: |
| Tradicional | 12/12 | 100 % | 0 |
| Generativo | 11/12 | 91.7 % | 0 |

El generativo clasificó como `ACCESS` un caso ambiguo etiquetado como `BUG`. También existieron diferencias de prioridad entre ambos motores, pero **la exactitud informada evalúa solamente categorías**, no la calidad de las respuestas ni la prioridad. Ambos motores solicitaron revisión humana en los cuatro casos clasificados como `SECURITY` dentro de la comparación.

Consulta la [metodología de comparación](docs/comparison-methodology.md) y la [evidencia JSON de la ejecución](artifacts/comparison_results.json).

## 12. Seguridad y limitaciones

- Nunca subir claves de Groq, archivos `.env` con datos reales ni información privada de usuarios.
- El archivo `.gitignore` excluye `.env`, entornos virtuales y archivos temporales habituales.
- Un resultado clasificado como `SECURITY` siempre debe revisarse por una persona.
- El motor tradicional se apoya en expresiones conocidas; puede no reconocer mensajes redactados de otra manera y asigna `BUG` por defecto cuando no detecta coincidencias.
- El motor generativo depende de la disponibilidad del proveedor y puede producir clasificaciones distintas entre ejecuciones.
- La comparación se realizó con 12 mensajes sintéticos y una sola ejecución. El 100 % del tradicional no demuestra que sea superior para todos los casos.
- No se midieron tiempos de respuesta, costos del proveedor ni exactitud de la prioridad. No deben afirmarse mejoras en esas dimensiones.
- Las pruebas de mensajes adversariales cubren ejemplos concretos, no garantizan seguridad absoluta.

## 13. Conclusión

El proyecto permite recibir solicitudes de soporte y procesarlas con dos motores diferentes mediante una misma API. El tradicional ofrece un comportamiento reproducible para los patrones definidos, mientras que el generativo permite interpretar mensajes utilizando un modelo externo. Los dos comparten el contrato JSON y aplican la regla de revisión humana para incidentes de seguridad. La evaluación y el código demuestran el funcionamiento del prototipo dentro del alcance probado, pero se necesita un conjunto de pruebas más amplio para sacar conclusiones generales.

## 14. Flujo de integración y entrega

Durante el desarrollo, las ramas de trabajo deben partir de `development` y sus PR deben fusionarse a `development` después de las pruebas y la revisión del equipo. Una vez completados el README, el informe de cierre y las correcciones, se abrirá un PR **de `development` hacia `main`**. La versión entregada al profesor debe ser la versión final de `main`, con documentación y evidencias coherentes con el código.
