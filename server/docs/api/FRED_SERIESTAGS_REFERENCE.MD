# FRED Series Tags Tool – API Reference
## Tool: get_fred_series_tags

Herramienta para obtener todos los tags asociados a una serie FRED específica. Te permite descubrir qué atributos (frecuencia, geografía, fuente, estacionalidad, etc.) FRED le asignó a una serie en particular. Útil para entender la categorización y metadatos de cualquier serie.

## Parámetros

### Parámetros requeridos

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `series_id` | string | **REQUERIDO**. El ID de la serie FRED. Ejemplos: "STLFSI", "GDP", "UNRATE", "CPIAUCSL" |

### Parámetros opcionales

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `order_by` | string | `"series_count"` | Campo por el que ordenar los tags. Ver valores válidos abajo. |
| `sort_order` | string | `"desc"` | Dirección de orden: "asc" (ascendente) o "desc" (descendente). |
| `realtime_start` | string | hoy | Inicio de ventana de real-time (YYYY-MM-DD). |
| `realtime_end` | string | hoy | Fin de ventana de real-time (YYYY-MM-DD). |

## Valores válidos

### order_by

- **series_count** (default) – Cantidad de series que tienen ese tag
- **popularity** – Score de popularidad de FRED
- **created** – Fecha de creación del tag
- **name** – Nombre alfabético del tag
- **group_id** – ID del grupo al que pertenece

### sort_order

- **asc** – Ascendente (menor a mayor)
- **desc** – Descendente (mayor a menor)

## Formato de respuesta

```json
{
  "tool": "get_series_tags",
  "data": [
    {
      "name": "nation",
      "group_id": "geot",
      "notes": "Country Level",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 105200
    },
    {
      "name": "usa",
      "group_id": "geo",
      "notes": "United States of America",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 100,
      "series_count": 393339
    },
    {
      "name": "weekly",
      "group_id": "freq",
      "notes": "",
      "created": "2012-02-27 10:18:19-06",
      "popularity": 75,
      "series_count": 21509
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "series_id": "STLFSI",
    "total_count": 8,
    "returned_count": 8,
    "order_by": "series_count",
    "sort_order": "desc",
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

## Observaciones

- **Compact JSON**: La respuesta usa formato compacto (sin espacios) para optimizar tokens en LLMs
- **Metadata completa**: Incluye fecha de fetch, series_id usado, conteo total y parámetros aplicados
- **Tags array**: Los tags vienen en el campo `data` para consistencia con otras herramientas
- **Real-time window**: Por defecto usa la fecha actual, pero podés consultar tags históricos

## Ejemplos de uso

### 1. Obtener tags de una serie específica (uso básico)

```python
get_fred_series_tags("STLFSI")
```

**Resultado**: Lista de todos los tags asignados al St. Louis Financial Stress Index, ordenados por cantidad de series.

### 2. Ver tags de GDP ordenados por popularidad

```python
get_fred_series_tags(
    "GDP",
    order_by="popularity",
    sort_order="desc"
)
```

**Resultado**: Tags del GDP ordenados de más a menos populares.

### 3. Ver tags de desempleo (unemployment rate)

```python
get_fred_series_tags("UNRATE")
```

**Resultado**: Descubrirás tags como:
- `sa` (seasonally adjusted)
- `monthly` (frequency)
- `usa` (geography)
- `bls` (source)
- `nation` (geography type)

### 4. Consulta con ventana real-time histórica

```python
get_fred_series_tags(
    "CPIAUCSL",
    realtime_start="2020-01-01",
    realtime_end="2020-12-31",
    order_by="name",
    sort_order="asc"
)
```

**Resultado**: Tags del CPI como existían durante el año 2020, ordenados alfabéticamente.

### 5. Ver tags de una serie ordenados por fecha de creación

```python
get_fred_series_tags(
    "UNRATE",
    order_by="created",
    sort_order="asc"
)
```

**Resultado**: Tags más antiguos primero, útil para entender la evolución de la categorización.

### 6. Analizar tags de una serie financiera

```python
get_fred_series_tags("DFF")  # Federal Funds Rate
```

**Resultado**: Descubrirás tags como:
- `daily` (frequency)
- `frb` (Federal Reserve Board - source)
- `interest rate` (concept)
- `usa` (geography)

### 7. Ver todos los tags alfabéticamente

```python
get_fred_series_tags(
    "GDP",
    order_by="name",
    sort_order="asc"
)
```

## Casos de uso

### 1. Exploración de series
**Escenario**: No sabés qué características tiene una serie.

**Solución**:
```python
tags = get_fred_series_tags("SERIES_ID")
# Descubrís: frecuencia, geografía, fuente, ajuste estacional
```

### 2. Filtrado inteligente
**Escenario**: Querés buscar series similares a una que ya conocés.

**Solución**:
```python
# Paso 1: Ver qué tags tiene una serie que te gusta
tags = get_fred_series_tags("UNRATE")
# Descubrís: monthly, sa, usa, bls

# Paso 2: Usar esos tags para buscar series similares
similar = get_fred_series_by_tags("monthly;sa;usa;bls")
```

### 3. Validación de series
**Escenario**: Necesitás confirmar que una serie tiene las características esperadas.

**Solución**:
```python
tags = get_fred_series_tags("GDP")
# Verificás que tenga: quarterly, sa, usa, bea
```

### 4. Construcción de queries
**Escenario**: Querés construir búsquedas multi-tag precisas.

**Solución**:
```python
# Descubrí tags de series conocidas
gdp_tags = get_fred_series_tags("GDP")
cpi_tags = get_fred_series_tags("CPIAUCSL")

# Identificá tags comunes y útiles
# Luego úsalos en búsquedas combinadas
```

### 5. Análisis de metadatos
**Escenario**: Estás documentando o auditando series en uso.

**Solución**:
```python
for series_id in ["GDP", "UNRATE", "CPIAUCSL"]:
    tags = get_fred_series_tags(series_id)
    # Genera reporte con frecuencia, fuente, ajuste
```

## Diferencias con otras herramientas

### vs. `get_fred_tags`
- **get_fred_tags**: Descubre qué tags existen en FRED (exploración global)
- **get_fred_series_tags**: Ve qué tags tiene UNA serie específica (exploración local)

### vs. `search_fred_series_tags`
- **search_fred_series_tags**: Tags para series que coinciden con una búsqueda de texto
- **get_fred_series_tags**: Tags de UNA serie específica por su ID

## Integración con otras herramientas

### Workflow típico

```python
# 1. Buscar series por texto
series = search_fred_series("unemployment")

# 2. Ver tags de una serie interesante
tags = get_fred_series_tags("UNRATE")

# 3. Usar tags descubiertos para búsqueda precisa
refined = get_fred_series_by_tags("monthly;sa;usa;bls")
```

## Grupos de tags que encontrarás

- **freq** (Frecuencia): daily, weekly, monthly, quarterly, annual
- **geo** (Geografía): usa, canada, japan, california, texas
- **geot** (Tipo geográfico): nation, state, county, msa
- **src** (Fuente): bls, bea, census, frb, oecd
- **seas** (Estacionalidad): sa, nsa
- **gen** (General/Concepto): gdp, employment, inflation, interest rate

## Notas técnicas

### Performance
- **Response time**: ~0.5-1.5 segundos típico
- **Compact JSON**: Ahorra ~25% de tokens vs. pretty-print
- **Retry mechanism**: 3 intentos con espera exponencial (1-5s)

### Rate limits
- FRED API: ~120 requests/minuto
- Retry automático en caso de límite
- Logging de operación en INFO level

### Errores comunes

#### Series ID inválido
```json
{
  "tool": "get_series_tags",
  "error": "Series not found: INVALID_ID",
  "series_id": "INVALID_ID"
}
```

#### API key faltante
```json
{
  "tool": "get_series_tags",
  "error": "Invalid parameters: API key is required",
  "series_id": "GDP"
}
```

## Endpoint FRED

```
https://api.stlouisfed.org/fred/series/tags
```

**Documentación oficial**: https://fred.stlouisfed.org/docs/api/fred/series_tags.html

## Changelog de la herramienta

- **v0.1.6** (2025-11-01): Implementación inicial de `get_fred_series_tags`

---

**Versión del documento**: 1.0
**Última actualización**: 2025-11-01
**Aplica a**: Trabajo IA MCP Server v0.1.6+
