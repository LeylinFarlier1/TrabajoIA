# Migration Guide - Nueva Estructura del Proyecto

## Resumen de Cambios

Este documento describe la reorganización completa del proyecto **Trabajo IA MCP Server** hacia una estructura profesional y moderna.

## Estructura Anterior vs Nueva

### Antes (Estructura Antigua)
```
server/
├── helpers/
│   └── tools/
│       └── FRED/
│           └── FETCH/
│               └── fetch_series_observations.py
├── main/
│   └── main.py
├── trabajo_ia.py
└── pyproject.toml
```

### Después (Estructura Nueva - src-layout)
```
server/
├── src/
│   ├── __main__.py
│   └── trabajo_ia_server/
│       ├── __init__.py
│       ├── server.py
│       ├── config.py
│       ├── tools/
│       │   └── fred/
│       │       └── fetch_series.py
│       ├── models/
│       └── utils/
│           ├── logger.py
│           └── validators.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
├── config/
│   └── .env.example
├── docs/
│   ├── architecture.md
│   ├── api/
│   └── guides/
├── pyproject.toml
└── README.md
```

## Cambios Principales

### 1. Adopción de src-layout
- Todo el código fuente ahora está en `src/trabajo_ia_server/`
- Previene imports accidentales desde el directorio de desarrollo
- Facilita el empaquetado y distribución

### 2. Nomenclatura Consistente
- **Antes**: `helpers/tools/FRED/FETCH/` (mezcla de mayúsculas/minúsculas)
- **Después**: `src/trabajo_ia_server/tools/fred/` (todo minúsculas, pythonic)

### 3. Separación de Responsabilidades

#### Configuración Centralizada
- **Antes**: Carga de `.env` dispersa en múltiples archivos
- **Después**: `config.py` - Singleton de configuración centralizada

```python
# Uso anterior
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("FRED_API_KEY")

# Uso nuevo
from trabajo_ia_server.config import config
api_key = config.get_fred_api_key()
```

#### Logging Unificado
- **Antes**: `logging.getLogger(__name__)` sin configuración
- **Después**: `utils/logger.py` con configuración estandarizada

```python
# Uso nuevo
from trabajo_ia_server.utils.logger import setup_logger
logger = setup_logger(__name__)
```

#### Validación de Inputs
- **Antes**: Sin validación explícita
- **Después**: `utils/validators.py` - Funciones de validación reutilizables

### 4. Estructura de Tests
- **Nuevo**: `tests/` con organización por tipo
  - `unit/` - Tests unitarios
  - `integration/` - Tests de integración
  - `fixtures/` - Datos de prueba

### 5. Documentación Mejorada
- **README.md** completo con ejemplos y guías
- **docs/architecture.md** - Documentación arquitectónica detallada
- **MIGRATION_GUIDE.md** - Este archivo

### 6. Configuración de Proyecto Mejorada

#### pyproject.toml actualizado
- Metadata completa del proyecto
- Dependencias de desarrollo (`dev`)
- Script de entrada: `trabajo-ia-server`
- Configuración de herramientas (pytest, mypy, ruff)

```toml
[project.scripts]
trabajo-ia-server = "trabajo_ia_server.server:main"

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "mypy", "ruff"]
```

## Mapeo de Archivos

| Archivo Anterior | Archivo Nuevo | Cambios |
|-----------------|---------------|---------|
| `trabajo_ia.py` | `src/__main__.py` | Simplificado, sin manipulación de sys.path |
| `main/main.py` | `src/trabajo_ia_server/server.py` | Imports actualizados, validación de config |
| `helpers/tools/FRED/FETCH/fetch_series_observations.py` | `src/trabajo_ia_server/tools/fred/fetch_series.py` | Validación agregada, mejor manejo de errores |
| N/A | `src/trabajo_ia_server/config.py` | **NUEVO** - Gestión centralizada de configuración |
| N/A | `src/trabajo_ia_server/utils/logger.py` | **NUEVO** - Logging estandarizado |
| N/A | `src/trabajo_ia_server/utils/validators.py` | **NUEVO** - Validación de inputs |

## Cómo Usar el Nuevo Sistema

### Instalación y Setup

1. **Sincronizar dependencias**:
   ```bash
   cd server
   uv sync
   ```

2. **Configurar variables de entorno**:
   ```bash
   cp config/.env.example .env
   # Editar .env y agregar FRED_API_KEY
   ```

### Ejecutar el Servidor

```bash
# Método 1: Como módulo Python
python -m trabajo_ia_server

# Método 2: Con UV
uv run python -m trabajo_ia_server

# Método 3: Script instalado (después de uv sync)
trabajo-ia-server
```

### Desarrollo

```bash
# Instalar dependencias de desarrollo
uv sync --extra dev

# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=trabajo_ia_server

# Verificar tipos
mypy src/trabajo_ia_server

# Linting y formateo
ruff check src/
ruff format src/
```

### Importar Módulos

```python
# Importar servidor
from trabajo_ia_server import mcp, main

# Importar herramientas
from trabajo_ia_server.tools.fred import fetch_series_observations

# Importar configuración
from trabajo_ia_server.config import config

# Importar utilidades
from trabajo_ia_server.utils.logger import setup_logger
from trabajo_ia_server.utils.validators import validate_date_format
```

## Beneficios de la Nueva Estructura

### 1. Mantenibilidad
- Código organizado por funcionalidad
- Separación clara de responsabilidades
- Fácil navegación y comprensión

### 2. Escalabilidad
- Fácil agregar nuevas herramientas
- Estructura modular para nuevas funcionalidades
- Preparado para crecimiento del proyecto

### 3. Profesionalismo
- Sigue mejores prácticas de Python
- Estructura reconocible para otros desarrolladores
- Facilita contribuciones externas

### 4. Testing
- Estructura de tests organizada
- Fixtures reutilizables
- Configuración de pytest incluida

### 5. Documentación
- README completo
- Documentación arquitectónica
- Guías de desarrollo

### 6. Herramientas de Desarrollo
- Configuración de linting (ruff)
- Type checking (mypy)
- Testing automatizado (pytest)
- Cobertura de código

## Migración de Código Personalizado

Si has modificado el código anterior, aquí está cómo migrar tus cambios:

### 1. Modificaciones en fetch_series_observations
```python
# Ubicación anterior
helpers/tools/FRED/FETCH/fetch_series_observations.py

# Ubicación nueva
src/trabajo_ia_server/tools/fred/fetch_series.py

# Actualizar imports:
# Antes:
from dotenv import load_dotenv
load_dotenv()

# Después:
from trabajo_ia_server.config import config
```

### 2. Nuevas Herramientas
```python
# Crear archivo en:
src/trabajo_ia_server/tools/fred/nueva_herramienta.py

# Registrar en server.py:
from trabajo_ia_server.tools.fred.nueva_herramienta import mi_funcion

@mcp.tool("mi_nueva_herramienta")
def mi_nueva_herramienta(...):
    return mi_funcion(...)
```

### 3. Configuración Adicional
```python
# Agregar en config.py:
class Config:
    # ...
    MI_NUEVA_VARIABLE: str = os.getenv("MI_NUEVA_VARIABLE")
```

## Archivos Eliminados

Los siguientes archivos/carpetas fueron eliminados:
- `helpers/` - Reemplazado por estructura modular
- `main/` - Integrado en `src/trabajo_ia_server/`
- `trabajo_ia.py` - Reemplazado por `src/__main__.py`

**Nota**: Si tenías cambios personalizados en estos archivos, revisa el código nuevo y migra tus cambios según las secciones anteriores.

## Solución de Problemas

### El servidor no encuentra el módulo trabajo_ia_server
```bash
# Asegúrate de haber sincronizado:
uv sync

# O instalar en modo editable con pip:
pip install -e .
```

### Error de FRED_API_KEY
```bash
# Verifica que .env existe y contiene:
FRED_API_KEY=tu_clave_aqui

# La configuración ahora valida al inicio
```

### Tests no funcionan
```bash
# Instalar dependencias de desarrollo:
uv sync --extra dev

# O con pip:
pip install -e ".[dev]"
```

## Próximos Pasos Recomendados

1. **Revisar la documentación**:
   - Leer `README.md` para uso general
   - Revisar `docs/architecture.md` para entender la arquitectura

2. **Ejecutar tests**:
   ```bash
   pytest
   ```

3. **Explorar el código**:
   - Revisar `src/trabajo_ia_server/server.py` para el servidor MCP
   - Revisar `src/trabajo_ia_server/tools/fred/fetch_series.py` para la herramienta FRED

4. **Agregar nuevas funcionalidades**:
   - Crear nuevas herramientas en `src/trabajo_ia_server/tools/`
   - Agregar tests en `tests/unit/`
   - Actualizar documentación

## Contacto y Soporte

Para preguntas o problemas con la migración:
- Revisar la documentación en `docs/`
- Verificar ejemplos en `tests/`
- Consultar el código fuente en `src/trabajo_ia_server/`

---

**Fecha de Migración**: 2025-11-01
**Versión**: 0.1.0
