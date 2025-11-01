# Guía Completa: Implementación de Nueva Tool FRED

**Versión:** 1.0
**Última actualización:** 2025-11-01
**Autor:** Sistema de documentación automática

---

## 📋 Índice

1. [Análisis del Proyecto Actual](#análisis-del-proyecto-actual)
2. [Arquitectura y Patrones](#arquitectura-y-patrones)
3. [Paso a Paso para Implementar Nueva Tool](#paso-a-paso-para-implementar-nueva-tool)
4. [Checklist de Verificación](#checklist-de-verificación)
5. [Ejemplos de Referencia](#ejemplos-de-referencia)

---

## 📊 Análisis del Proyecto Actual

### Estructura del Proyecto

```
server/
├── src/trabajo_ia_server/
│   ├── __init__.py              # Versión del paquete
│   ├── config.py                # Configuración centralizada
│   ├── server.py                # Servidor MCP principal
│   ├── tools/
│   │   └── fred/
│   │       ├── __init__.py      # Exports de las tools
│   │       ├── fetch_series.py  # Tool 1: Fetch observations
│   │       ├── search_series.py # Tool 2: Search series
│   │       ├── get_tags.py      # Tool 3: Get tags
│   │       └── related_tags.py  # Tool 4: Related tags
│   └── utils/
│       ├── logger.py            # Sistema de logging
│       └── validators.py        # Validadores de datos
├── docs/
│   ├── api/                     # Referencias API detalladas
│   │   ├── FRED_SEARCH_REFERENCE.md
│   │   ├── FRED_TAGS_REFERENCE.MD
│   │   └── FRED_RELATEDTAGS_REFERENCE.MD
│   ├── Changelog/
│   │   └── CHANGELOG.md         # Historial de cambios
│   └── Release_notes/
│       ├── RELEASE_NOTES_v0.1.1.md
│       ├── RELEASE_NOTES_v0.1.2.md
│       └── RELEASE_NOTES_v0.1.3.md
└── pyproject.toml               # Configuración del proyecto
```

### Tools Actuales Implementadas

| Tool | Archivo | Endpoint FRED | Propósito |
|------|---------|---------------|-----------|
| `fetch_fred_series` | `fetch_series.py` | `/fred/series/observations` | Obtener datos históricos de una serie |
| `search_fred_series` | `search_series.py` | `/fred/series/search` | Buscar series por texto/filtros |
| `get_fred_tags` | `get_tags.py` | `/fred/tags` | Descubrir tags disponibles |
| `search_fred_related_tags` | `related_tags.py` | `/fred/related_tags` | Encontrar tags relacionados |

### Versión Actual

- **Versión del servidor:** 0.1.3
- **Python:** >= 3.10
- **Framework MCP:** FastMCP (mcp[cli] >= 1.20.0)
- **FRED API:** Sin versión (API estable)

---

## 🏗️ Arquitectura y Patrones

### Patrón de Implementación Establecido

Todas las tools FRED siguen un patrón consistente:

#### 1. **Estructura del Archivo de Tool**

```python
"""
[Título de la Tool].

[Descripción breve de qué hace la tool].
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint
FRED_[NOMBRE]_URL = "https://api.stlouisfed.org/fred/[endpoint]"

# Función de retry helper
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _request_with_retries(url: str, params: dict) -> requests.Response:
    """Make HTTP request with retry logic."""
    session = requests.Session()
    try:
        response = session.get(url, params=params, timeout=30)

        if response.status_code == 429:
            logger.warning("Rate limit hit, retrying...")
            raise requests.exceptions.RequestException("Rate limit exceeded")

        response.raise_for_status()
        return response
    finally:
        session.close()

# Función principal de la tool
def [nombre_tool](
    parametro1: str,
    parametro2: Optional[str] = None,
    # ... más parámetros
) -> str:
    """
    [Docstring detallado].

    Args:
        parametro1: Descripción
        parametro2: Descripción

    Returns:
        JSON string con datos y metadata

    Examples:
        >>> [nombre_tool]("ejemplo")
    """
    try:
        # 1. Obtener API key
        api_key = config.get_fred_api_key()

        # 2. Validar y procesar parámetros
        # ...

        # 3. Construir parámetros de request
        params = {
            "api_key": api_key,
            "file_type": "json",
            # ... más params
        }

        # 4. Logging
        logger.info(f"[Mensaje descriptivo de la operación]")

        # 5. Hacer request
        response = _request_with_retries(FRED_[NOMBRE]_URL, params)
        json_data = response.json()

        # 6. Procesar respuesta
        data = json_data.get("[campo_principal]", [])

        # 7. Construir output
        output = {
            "tool": "[nombre_tool]",
            "data": data,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                # ... más metadata
            }
        }

        logger.info(f"[Mensaje de éxito]")

        # 8. Retornar JSON compacto (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        # Manejo de errores HTTP
        error_msg = f"FRED API error: {e.response.status_code}"
        # ... manejo específico
        logger.error(error_msg)
        return json.dumps({
            "tool": "[nombre_tool]",
            "error": error_msg,
        }, separators=(",", ":"))

    except Exception as e:
        # Manejo de errores genéricos
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "[nombre_tool]",
            "error": error_msg,
        }, separators=(",", ":"))
```

#### 2. **Registro en server.py**

```python
# Importar la función
from trabajo_ia_server.tools.fred.[archivo] import [nombre_funcion]

# Registrar como tool MCP
@mcp.tool("[nombre_tool]")
def [nombre_wrapper](
    parametro1: str,
    parametro2: Optional[str] = None,
    # ... parámetros con types exactos
) -> str:
    """
    [Docstring para el usuario MCP].

    Args:
        parametro1: Descripción user-friendly
        parametro2: Descripción user-friendly

    Returns:
        JSON con datos y metadata

    Examples:
        >>> [nombre_wrapper]("ejemplo")
    """
    logger.info(f"[Mensaje de log]")
    return [nombre_funcion](
        parametro1=parametro1,
        parametro2=parametro2,
        # ... todos los params
    )
```

#### 3. **Export en __init__.py**

```python
from trabajo_ia_server.tools.fred.[archivo] import [nombre_funcion]

__all__ = [
    "fetch_series_observations",
    "search_fred_series",
    "get_fred_tags",
    "search_fred_related_tags",
    "[nombre_funcion]",  # Nueva tool
]
```

### Características Técnicas Obligatorias

✅ **Performance optimizado para AI/LLM:**
- JSON siempre compacto: `separators=(",", ":")`
- Límites por defecto razonables (20-50 items)
- Sin paginación (single request)
- Retry rápido: 3 intentos, 1-5s exponential backoff

✅ **Manejo de errores robusto:**
- Try/except para HTTPError y Exception
- Rate limit detection (429) con retry
- Mensajes de error informativos
- Logging completo

✅ **Metadata completa:**
- `fetch_date`: Timestamp UTC ISO 8601
- Parámetros usados en el request
- Counts (total, returned)
- Información de filtros aplicados

✅ **Type hints completos:**
- Usar `Literal` para enums
- `Optional` para parámetros opcionales
- Return type siempre `str` (JSON string)

✅ **Documentación:**
- Docstring detallado con Args, Returns, Examples
- Logging informativo (INFO para operaciones, ERROR para fallos)

---

## 🔧 Paso a Paso para Implementar Nueva Tool

### FASE 0: Preparación

#### Input Necesario del Usuario:

```
El usuario debe proveer:

1. INFORMACIÓN DE LA API:
   - Endpoint FRED: /fred/[endpoint]
   - Parámetros requeridos
   - Parámetros opcionales
   - Formato de respuesta
   - Ejemplos de uso

2. PROPÓSITO DE LA TOOL:
   - Qué hace la herramienta
   - Casos de uso principales
   - Valor que aporta

3. NOMBRE DE LA TOOL:
   - Nombre de la función: [nombre_funcion]
   - Nombre del archivo: [archivo].py
   - Nombre MCP tool: [nombre_tool]
```

---

### FASE 1: Crear Archivo de Tool

**Archivo:** `src/trabajo_ia_server/tools/fred/[archivo].py`

#### Paso 1.1: Crear TodoWrite

```python
TodoWrite([
    {"content": "Crear [archivo].py con implementación", "status": "in_progress"},
    {"content": "Registrar tool en server.py", "status": "pending"},
    {"content": "Exportar en __init__.py", "status": "pending"},
    {"content": "Crear documentación API reference", "status": "pending"},
    {"content": "Probar la tool", "status": "pending"},
])
```

#### Paso 1.2: Escribir el archivo completo

**Plantilla a seguir:**

```python
"""
[Título Descriptivo de la Tool].

[Descripción de 2-3 líneas del propósito de la tool].
"""
import json
import logging
from datetime import datetime
from typing import Literal, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from trabajo_ia_server.config import config

logger = logging.getLogger(__name__)

# FRED API endpoint para [funcionalidad]
FRED_[NOMBRE_CONSTANTE]_URL = "https://api.stlouisfed.org/fred/[endpoint]"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
)
def _request_with_retries(url: str, params: dict) -> requests.Response:
    """Make HTTP request with retry logic for transient failures."""
    session = requests.Session()
    try:
        response = session.get(url, params=params, timeout=30)

        if response.status_code == 429:
            logger.warning("Rate limit hit, retrying...")
            raise requests.exceptions.RequestException("Rate limit exceeded")

        response.raise_for_status()
        return response
    finally:
        session.close()


def [nombre_funcion](
    # REQUERIDOS primero
    [param_requerido]: [tipo],
    # OPCIONALES después
    [param_opcional]: Optional[[tipo]] = None,
    # Parámetros comunes de FRED
    limit: int = [default_apropiado],
    offset: int = 0,
    order_by: Literal[[valores]] = "[default]",
    sort_order: Literal["asc", "desc"] = "[default]",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    [Descripción detallada de qué hace la tool].

    [Párrafo adicional explicando casos de uso].

    Args:
        [param_requerido]: Descripción clara del parámetro.
                          Ejemplo: "gdp" o "usa;employment"
        [param_opcional]: Descripción del parámetro opcional.
        limit: Maximum results (1-1000). Default: [N].
        offset: Starting offset for pagination. Default: 0.
        order_by: Sort field. Options: [...]. Default: "[default]".
        sort_order: Sort direction - "asc" or "desc". Default: "[default]".
        realtime_start: Start date for real-time period (YYYY-MM-DD).
        realtime_end: End date for real-time period (YYYY-MM-DD).

    Returns:
        JSON string with [tipo de datos] and metadata.

    Response Format:
        {
            "tool": "[nombre_tool]",
            "data": [
                {
                    "[campo1]": "valor",
                    "[campo2]": "valor",
                    ...
                }
            ],
            "metadata": {
                "fetch_date": "2025-11-01T12:00:00Z",
                "total_count": 100,
                "returned_count": 50,
                ...
            }
        }

    Examples:
        # Ejemplo básico
        [nombre_funcion]("[valor_simple]")

        # Con filtros
        [nombre_funcion]("[valor]", [param_opcional]="[valor]")

        # Completo
        [nombre_funcion](
            "[valor]",
            [param_opcional]="[valor]",
            limit=20,
            order_by="[criterio]"
        )
    """
    try:
        # 1. Obtener API key
        api_key = config.get_fred_api_key()

        # 2. Validar parámetros (si es necesario)
        limit = max(1, min(limit, 1000))  # Clamp limit

        # 3. Construir parámetros base
        params = {
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "sort_order": sort_order,
        }

        # 4. Agregar parámetros requeridos
        params["[nombre_param_api]"] = [param_requerido]

        # 5. Agregar parámetros opcionales
        if [param_opcional]:
            params["[nombre_param_api]"] = [param_opcional]
        if realtime_start:
            params["realtime_start"] = realtime_start
        if realtime_end:
            params["realtime_end"] = realtime_end

        # 6. Log de operación
        logger.info(
            f"[Descripción de la operación]: '[valores_clave]'"
        )

        # 7. Hacer request con retry
        response = _request_with_retries(FRED_[NOMBRE]_URL, params)
        json_data = response.json()

        # 8. Extraer datos principales
        data = json_data.get("[campo_principal]", [])

        # 9. Construir output estructurado
        output = {
            "tool": "[nombre_tool]",
            "data": data,
            "metadata": {
                "fetch_date": datetime.utcnow().isoformat() + "Z",
                "[param_usado]": [param_requerido],
                "[param_opcional_key]": [param_opcional],
                "total_count": json_data.get("[campo_count]", len(data)),
                "returned_count": len(data),
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
                "sort_order": sort_order,
                "realtime_start": json_data.get("realtime_start"),
                "realtime_end": json_data.get("realtime_end"),
            },
        }

        # 10. Log de éxito
        logger.info(f"[Mensaje de éxito]: {len(data)} [items]")

        # 11. Retornar JSON compacto (AI-optimized)
        return json.dumps(output, separators=(",", ":"), default=str)

    except requests.exceptions.HTTPError as e:
        # Manejo de errores HTTP específicos
        error_msg = f"FRED API error: {e.response.status_code}"

        if e.response.status_code == 400:
            try:
                error_detail = e.response.json().get("error_message", "Bad request")
                error_msg = f"Invalid parameters: {error_detail}"
            except Exception:
                error_msg = "Invalid parameters provided"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again later."

        logger.error(error_msg)
        return json.dumps({
            "tool": "[nombre_tool]",
            "error": error_msg,
            "[param_context]": [param_requerido],
        }, separators=(",", ":"))

    except Exception as e:
        # Manejo de errores genéricos
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({
            "tool": "[nombre_tool]",
            "error": error_msg,
            "[param_context]": [param_requerido] if [param_requerido] else None,
        }, separators=(",", ":"))
```

#### Paso 1.3: Actualizar TodoWrite

```python
TodoWrite([
    {"content": "Crear [archivo].py con implementación", "status": "completed"},
    {"content": "Registrar tool en server.py", "status": "in_progress"},
    ...
])
```

---

### FASE 2: Registrar en server.py

**Archivo:** `src/trabajo_ia_server/server.py`

#### Paso 2.1: Agregar import

```python
# En la sección de imports (línea ~15)
from trabajo_ia_server.tools.fred.[archivo] import [nombre_funcion]
```

#### Paso 2.2: Registrar tool MCP

```python
# Después de las tools existentes (antes de def main())

@mcp.tool("[nombre_tool]")
def [nombre_wrapper](
    [param_requerido]: [tipo],
    [param_opcional]: Optional[[tipo]] = None,
    # ... TODOS los parámetros con tipos EXACTOS
    limit: int = [default],
    offset: int = 0,
    order_by: Literal[[valores]] = "[default]",
    sort_order: Literal["asc", "desc"] = "[default]",
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    [Título user-friendly de la tool].

    [Descripción en términos que entienda el usuario/AI].
    [Párrafo adicional sobre casos de uso].

    Args:
        [param_requerido]: [Descripción clara].
        [param_opcional]: [Descripción clara] (optional).
        limit: Max results (1-1000, default: [N] - optimized for AI).
        offset: Starting offset (default: 0).
        order_by: Sort field (default: "[default]").
            - "[opcion1]": [Descripción]
            - "[opcion2]": [Descripción]
        sort_order: "asc" or "desc" (default: "[default]").
        realtime_start: Real-time start date YYYY-MM-DD (optional).
        realtime_end: Real-time end date YYYY-MM-DD (optional).

    Returns:
        Compact JSON with [descripción de datos] and metadata.

    Examples:
        >>> [nombre_wrapper]("[ejemplo1]")
        >>> [nombre_wrapper]("[ejemplo2]", [param]="[valor]")
        >>> [nombre_wrapper]("[ejemplo3]", limit=20, order_by="[criterio]")
    """
    logger.info(f"[Mensaje descriptivo con valores clave]")
    return [nombre_funcion](
        [param_requerido]=[param_requerido],
        [param_opcional]=[param_opcional],
        limit=limit,
        offset=offset,
        order_by=order_by,
        sort_order=sort_order,
        realtime_start=realtime_start,
        realtime_end=realtime_end,
    )
```

#### Paso 2.3: Verificar sintaxis

```bash
cd server && uv run python -c "from trabajo_ia_server.server import mcp"
```

#### Paso 2.4: Actualizar TodoWrite

```python
TodoWrite([
    ...,
    {"content": "Registrar tool en server.py", "status": "completed"},
    {"content": "Exportar en __init__.py", "status": "in_progress"},
    ...
])
```

---

### FASE 3: Exportar en __init__.py

**Archivo:** `src/trabajo_ia_server/tools/fred/__init__.py`

#### Paso 3.1: Agregar import

```python
from trabajo_ia_server.tools.fred.[archivo] import [nombre_funcion]
```

#### Paso 3.2: Agregar a __all__

```python
__all__ = [
    "fetch_series_observations",
    "search_fred_series",
    "get_fred_tags",
    "search_fred_related_tags",
    "[nombre_funcion]",  # Nueva tool
]
```

#### Paso 3.3: Actualizar TodoWrite

```python
TodoWrite([
    ...,
    {"content": "Exportar en __init__.py", "status": "completed"},
    {"content": "Crear documentación API reference", "status": "in_progress"},
    ...
])
```

---

### FASE 4: Crear Documentación API Reference

**Archivo:** `docs/api/FRED_[NOMBRE]_REFERENCE.MD`

#### Paso 4.1: Verificar que el archivo NO exista (o leerlo primero)

```python
# IMPORTANTE: Siempre leer el archivo primero si existe
Read("C:\\Users\\agust\\OneDrive\\Documentos\\VSCODE\\trabajoIA\\server\\docs\\api\\FRED_[NOMBRE]_REFERENCE.MD")
```

#### Paso 4.2: Crear documentación completa

**Estructura obligatoria del documento:**

```markdown
# FRED [Nombre] API Reference

**Tool Name:** `[nombre_tool]`

**Endpoint:** `https://api.stlouisfed.org/fred/[endpoint]`

**Description:** [Descripción de 2-3 líneas].

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Error Handling](#error-handling)
7. [Performance](#performance)
8. [Best Practices](#best-practices)
9. [Related Tools](#related-tools)

---

## Overview

[Descripción detallada de qué hace la tool].

### Key Features

- **Feature 1**: Descripción
- **Feature 2**: Descripción
- **Feature 3**: Descripción
- **AI-optimized**: Compact JSON, fast responses

---

## Parameters

### Required Parameters

#### `[param_requerido]` ([tipo], REQUIRED)

[Descripción detallada].

**Format:** `"[formato]"`

**Examples:**
```python
"[ejemplo1]"
"[ejemplo2]"
```

**Important Notes:**
- Nota 1
- Nota 2

---

### Optional Parameters

#### `[param_opcional]` ([tipo], optional)

[Descripción].

**Default:** [valor]

**Examples:**
```python
[param_opcional]="[ejemplo]"
```

---

[... más parámetros siguiendo el mismo patrón ...]

---

## Response Format

### Success Response

```json
{
  "tool": "[nombre_tool]",
  "data": [
    {
      "[campo1]": "valor",
      "[campo2]": "valor"
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "total_count": 100,
    "returned_count": 50
  }
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| `[campo1]` | [tipo] | [Descripción] |
| `[campo2]` | [tipo] | [Descripción] |

---

## Usage Examples

### Example 1: [Título del ejemplo]

**Goal:** [Qué se quiere lograr]

```python
[nombre_tool]("[ejemplo]")
```

**Result:**
```json
{
  "data": [...]
}
```

**Insight:** [Qué aprendemos de este resultado]

---

[... mínimo 5-7 ejemplos ...]

---

## Use Cases

### 1. [Caso de uso 1]

**Problem:** [Problema]

**Solution:**
```python
# Paso 1
result = [nombre_tool]("[params]")

# Paso 2
# ...
```

---

[... mínimo 5 casos de uso ...]

---

## Error Handling

### Common Errors

#### [Tipo de error 1]

**Error:**
```json
{"error": "[mensaje]"}
```

**Cause:** [Causa]

**Fix:**
```python
# Solución
```

---

## Performance

### Response Time

- **Typical:** 0.5-1.0 seconds
- **With filters:** 0.5-1.5 seconds

### Optimization Tips

1. [Tip 1]
2. [Tip 2]

### Token Efficiency

**Compact JSON format:**
- Saves ~25% tokens
- Default limit ([N]) balances information density

---

## Best Practices

### 1. [Best practice 1]

```python
# Good
[ejemplo_bueno]

# Bad
[ejemplo_malo]
```

---

## Related Tools

### Complementary Tools

1. **`tool_1`**
   - [Relación]
   - **Use [before/after]** `[nombre_tool]`

2. **`tool_2`**
   - [Relación]

### Typical Workflow

```python
# Paso 1: [Tool previa]
step1 = tool_1("[params]")

# Paso 2: Esta tool
step2 = [nombre_tool]("[params]")

# Paso 3: [Tool siguiente]
step3 = tool_3("[params]")
```

---

## Version Information

- **Tool Version:** Introduced in v[X.Y.Z]
- **FRED API Version:** Uses FRED API
- **Last Updated:** [Fecha]

---

## Support & Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **Endpoint Docs:** https://fred.stlouisfed.org/docs/api/fred/[endpoint].html
- **FRED Homepage:** https://fred.stlouisfed.org/

---

## Summary

The `[nombre_tool]` tool is essential for:

✅ [Propósito 1]
✅ [Propósito 2]
✅ [Propósito 3]

**Key Strengths:**
- Fast, AI-optimized responses
- [Fortaleza 2]
- [Fortaleza 3]

**Best For:**
- [Uso ideal 1]
- [Uso ideal 2]
```

#### Paso 4.3: Actualizar TodoWrite

```python
TodoWrite([
    ...,
    {"content": "Crear documentación API reference", "status": "completed"},
    {"content": "Probar la tool", "status": "in_progress"},
])
```

---

### FASE 5: Probar la Tool

#### Paso 5.1: Crear script de prueba

```bash
cd server && uv run python -c "
from trabajo_ia_server.tools.fred.[archivo] import [nombre_funcion]
import json
import time

print('=== Testing [nombre_tool] ===\n')

# Test 1: Caso básico
print('Test 1: [Descripción]')
start = time.time()
result = [nombre_funcion]('[valor_prueba]')
elapsed = time.time() - start
data = json.loads(result)

if 'error' in data:
    print(f'  ERROR: {data[\"error\"]}')
else:
    print(f'  Time: {elapsed:.2f}s')
    print(f'  Results: {data[\"metadata\"][\"returned_count\"]}')
    print(f'  Total: {data[\"metadata\"][\"total_count\"]}')
    print(f'  Sample data: {data[\"data\"][:3]}')
print()

# Test 2: Con filtros
print('Test 2: [Descripción con filtros]')
start = time.time()
result = [nombre_funcion](
    '[valor]',
    [param_opcional]='[valor]',
    limit=10
)
elapsed = time.time() - start
data = json.loads(result)

if 'error' in data:
    print(f'  ERROR: {data[\"error\"]}')
else:
    print(f'  Time: {elapsed:.2f}s')
    print(f'  Results: {data[\"metadata\"][\"returned_count\"]}')
print()

# Test 3: Caso edge
print('Test 3: [Caso edge]')
start = time.time()
result = [nombre_funcion]('[valor_edge]')
elapsed = time.time() - start
data = json.loads(result)

if 'error' in data:
    print(f'  Expected error: {data[\"error\"]}')
else:
    print(f'  Unexpected success: {data[\"metadata\"][\"returned_count\"]} results')
print()

print('All tests completed!')
"
```

#### Paso 5.2: Verificar resultados

**Checklist de verificación:**

✅ Test 1 exitoso (caso básico)
✅ Test 2 exitoso (con filtros)
✅ Test 3 maneja errores correctamente
✅ Tiempos de respuesta < 2s
✅ JSON compacto (sin espacios)
✅ Metadata completa
✅ Logging visible en consola

#### Paso 5.3: Actualizar TodoWrite

```python
TodoWrite([
    ...,
    {"content": "Probar la tool", "status": "completed"},
])
```

---

### FASE 6: Verificación Final

#### Checklist Completo

```
✅ Archivo de tool creado en src/trabajo_ia_server/tools/fred/
✅ Imports correctos (json, logging, datetime, typing, requests, tenacity)
✅ Constante FRED_[NOMBRE]_URL definida
✅ Función _request_with_retries implementada
✅ Función principal con todos los parámetros
✅ Docstring completo con Args, Returns, Examples
✅ Try/except para HTTPError y Exception
✅ Logging en INFO y ERROR
✅ JSON compacto con separators=(",",":")
✅ Metadata completa con fetch_date, counts, params
✅ Retry con 3 intentos, 1-5s exponential backoff
✅ Rate limit detection (429)
✅ Type hints completos con Literal y Optional

✅ Tool registrada en server.py
✅ Import agregado
✅ @mcp.tool decorator
✅ Función wrapper con mismos parámetros
✅ Docstring user-friendly
✅ Logger.info call
✅ Return statement llamando función principal

✅ Export en tools/fred/__init__.py
✅ Import agregado
✅ Nombre en __all__

✅ Documentación API reference creada
✅ Archivo leído primero (si existía)
✅ Todas las secciones incluidas
✅ Mínimo 5-7 ejemplos
✅ Mínimo 5 casos de uso
✅ Error handling documentado
✅ Performance tips incluidos
✅ Best practices incluidas

✅ Tests ejecutados
✅ Test básico pasa
✅ Test con filtros pasa
✅ Test de errores maneja correctamente
✅ Tiempos < 2s
✅ JSON compacto verificado
✅ Logging visible
```

---

## 📚 Ejemplos de Referencia

### Ejemplo Completo: related_tags.py

Ver implementación en:
- `src/trabajo_ia_server/tools/fred/related_tags.py`
- `src/trabajo_ia_server/server.py` (líneas 182-240)
- `docs/api/FRED_RELATEDTAGS_REFERENCE.MD`

### Puntos Clave del Ejemplo

1. **Parámetro requerido:**
```python
def search_fred_related_tags(
    tag_names: str,  # REQUIRED - sin default
    ...
)
```

2. **Validación de parámetros:**
```python
limit = max(1, min(limit, 1000))  # Clamp limit
```

3. **Logging informativo:**
```python
logger.info(
    f"Fetching related tags for: '{tag_names}' "
    f"(group={tag_group_id}, search='{search_text}')"
)
```

4. **Metadata completa:**
```python
"metadata": {
    "fetch_date": datetime.utcnow().isoformat() + "Z",
    "input_tags": tag_names.split(";"),
    "excluded_tags": exclude_tag_names.split(";") if exclude_tag_names else None,
    "tag_group_id": tag_group_id,
    "total_count": json_data.get("count", len(tags)),
    "returned_count": len(tags),
    ...
}
```

5. **Error handling específico:**
```python
if e.response.status_code == 400:
    try:
        error_detail = e.response.json().get("error_message", "Bad request")
        error_msg = f"Invalid parameters: {error_detail}"
    except Exception:
        error_msg = "Invalid parameters provided"
```

---

## 🎯 Resumen del Proceso

### Workflow Simplificado

```
1. USUARIO provee:
   - Endpoint FRED
   - Parámetros
   - Propósito
   - Nombre de la tool

2. IA ejecuta:
   ├─ FASE 1: Crear [archivo].py (200+ líneas)
   ├─ FASE 2: Registrar en server.py (~60 líneas)
   ├─ FASE 3: Export en __init__.py (2 líneas)
   ├─ FASE 4: Documentación (~500-1000 líneas)
   └─ FASE 5: Testing (3 tests)

3. VERIFICACIÓN:
   ✓ Todos los checklists pasados
   ✓ Tests exitosos
   ✓ Documentación completa
```

### Tiempo Estimado

- **Fase 1:** 2-3 minutos (código)
- **Fase 2:** 1 minuto (registro)
- **Fase 3:** 30 segundos (export)
- **Fase 4:** 3-4 minutos (documentación)
- **Fase 5:** 1-2 minutos (testing)

**Total:** ~10 minutos por tool

---

## 📝 Plantilla de Request para Usuario

```markdown
# Nueva Tool FRED: [NOMBRE]

## 1. Información de la API

**Endpoint:** /fred/[endpoint]

**Documentación oficial:** [URL]

**Parámetros requeridos:**
- [param1]: [tipo] - [descripción]

**Parámetros opcionales:**
- [param2]: [tipo] - [descripción]
- [param3]: [tipo] - [descripción]

**Respuesta de la API:**
```json
{
  "[campo_principal]": [
    {
      "[campo1]": "valor",
      "[campo2]": "valor"
    }
  ]
}
```

## 2. Propósito de la Tool

[Descripción de qué hace la herramienta]

**Casos de uso:**
1. [Caso 1]
2. [Caso 2]
3. [Caso 3]

## 3. Nombres

- **Función:** [nombre_funcion] (ej: search_fred_related_tags)
- **Archivo:** [archivo].py (ej: related_tags.py)
- **MCP Tool:** [nombre_tool] (ej: search_fred_related_tags)

## 4. Ejemplos de Uso

```python
# Ejemplo básico
[nombre_tool]("[valor]")

# Con filtros
[nombre_tool]("[valor]", [param]="[valor]")
```
```

---

## ✅ Conclusión

Con esta guía, la implementación de una nueva tool FRED sigue un proceso:

1. **Sistemático** - Cada paso está claramente definido
2. **Consistente** - Todos los patrones son uniformes
3. **Completo** - Incluye código, registro, tests y documentación
4. **Verificable** - Checklists en cada fase
5. **Rápido** - ~10 minutos de principio a fin

**Próximos pasos:** El usuario proporciona la información de la API usando la plantilla, y la IA ejecuta las 5 fases automáticamente.
