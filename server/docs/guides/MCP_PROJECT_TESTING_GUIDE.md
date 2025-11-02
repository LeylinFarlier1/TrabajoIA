# Guía Completa: Entender el Proyecto MCP y Generar Prompts de Pruebas

**Versión:** 1.0  
**Fecha:** 2025-11-01  
**Propósito:** Guía paso a paso para entender el proyecto MCP Trabajo IA Server y generar prompts efectivos para probar tools individuales y workflows completos

---

## 📋 Tabla de Contenidos

1. [Introducción al Proyecto](#1-introducción-al-proyecto)
2. [Arquitectura MCP y Estructura](#2-arquitectura-mcp-y-estructura)
3. [Herramientas Disponibles (v0.1.9)](#3-herramientas-disponibles-v019)
4. [Cómo Funcionan las Herramientas](#4-cómo-funcionan-las-herramientas)
5. [Generando Prompts de Prueba Individual](#5-generando-prompts-de-prueba-individual)
6. [Diseñando Workflows Multi-Herramienta](#6-diseñando-workflows-multi-herramienta)
7. [Ejemplos de Workflows Completos](#7-ejemplos-de-workflows-completos)
8. [Patrones Comunes de Uso](#8-patrones-comunes-de-uso)
9. [Mejores Prácticas](#9-mejores-prácticas)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Introducción al Proyecto

### ¿Qué es este Proyecto?

**Trabajo IA MCP Server** es un servidor que implementa el **Model Context Protocol (MCP)** para proporcionar acceso completo a los datos económicos de **FRED (Federal Reserve Economic Data)** de manera estructurada y optimizada para IA/LLMs.

### Conceptos Clave

#### Model Context Protocol (MCP)
- **Protocolo** de comunicación estandarizado entre sistemas de IA y fuentes de datos
- Permite que los **LLMs accedan a datos externos** de forma estructurada
- Similar a una API, pero diseñado específicamente para IA

#### FRED (Federal Reserve Economic Data)
- Base de datos económicos de la Reserva Federal de EE.UU.
- **800,000+ series** de datos económicos
- Datos de: PIB, desempleo, inflación, tasas de interés, comercio, etc.
- **API gratuita** con clave de acceso

#### Tools (Herramientas)
- **Funciones** que el LLM puede llamar para obtener datos
- Cada tool hace una **tarea específica** (buscar, filtrar, obtener datos)
- 15 tools disponibles en este proyecto (v0.1.9): 14 FRED tools + 1 tool de salud del sistema

---

## 2. Arquitectura MCP y Estructura

### Diagrama de Flujo General

```
┌─────────────┐
│   Usuario   │
│  (Prompt)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│        LLM (IA Assistant)           │
│  Interpreta prompt y decide qué     │
│  herramientas usar                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    MCP Server (Este Proyecto)       │
│  - Recibe llamadas a herramientas   │
│  - Ejecuta funciones                │
│  - Llama a FRED API                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FRED API                     │
│  Devuelve datos económicos          │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Respuesta al Usuario              │
│  Datos formateados en JSON           │
└─────────────────────────────────────┘
```

### Estructura del Proyecto

```
server/
├── src/trabajo_ia_server/
│   ├── server.py                    # 🔧 Servidor MCP (registra tools)
│   ├── config.py                    # ⚙️  Configuración (API key, etc.)
│   ├── tools/fred/                  # 🛠️  Implementaciones de herramientas
│   │   ├── __init__.py             # Exports de las 15 tools registradas
│   │   ├── search_series.py        # Tool 1: Búsqueda de series
│   │   ├── get_tags.py             # Tool 2: Obtener tags
│   │   ├── related_tags.py         # Tool 3: Tags relacionados
│   │   ├── series_by_tags.py       # Tool 4: Series por tags
│   │   ├── search_series_tags.py   # Tool 5: Tags en búsqueda
│   │   ├── search_series_related_tags.py # Tool 6: Tags relacionados en búsqueda
│   │   ├── get_series_tags.py      # Tool 7: Tags de una serie
│   │   ├── observations.py         # Tool 8: Datos de series
│   │   ├── category.py             # Tool 9: Info de categoría
│   │   ├── category_children.py    # Tool 10: Subcategorías
│   │   ├── category_related.py     # Tool 11: Categorías relacionadas
│   │   ├── category_series.py      # Tool 12: Series en categoría
│   │   ├── category_tags.py        # Tool 13: Tags en categoría
│   │   └── category_related_tags.py # Tool 14: Tags relacionados en categoría
│   └── utils/
│       ├── logger.py               # Sistema de logging
│       └── validators.py           # Validadores
│
├── docs/
│   ├── api/                        # 📚 Documentación detallada de cada tool
│   ├── guides/                     # 📖 Guías (esta es una de ellas)
│   ├── Changelog/                  # 📝 Historial de cambios
│   └── Release_notes/              # 🎉 Notas de cada versión
│
├── tests/                          # 🧪 Pruebas unitarias
├── pyproject.toml                  # 📦 Configuración del proyecto
└── .env                            # 🔐 Variables de entorno (API key)
```

---

## 3. Herramientas Disponibles (v0.1.9)

### Clasificación por Función

#### 🔍 **Categoría 1: Búsqueda y Descubrimiento de Series**

| # | Tool | Función | Input Principal | Output |
|---|------|---------|-----------------|--------|
| 1 | `search_fred_series` | Buscar series por texto | Texto de búsqueda | Lista de series |
| 4 | `get_fred_series_by_tags` | Filtrar series por tags | Tags (AND/NOT logic) | Series con esos tags |

#### 🏷️ **Categoría 2: Exploración de Tags**

| # | Tool | Función | Input Principal | Output |
|---|------|---------|-----------------|--------|
| 2 | `get_fred_tags` | Descubrir todos los tags | (Opcional: filtros) | Lista de tags globales |
| 3 | `search_fred_related_tags` | Tags relacionados globales | Tags base | Tags relacionados |
| 5 | `search_fred_series_tags` | Tags en resultados de búsqueda | Texto + tags | Tags en ese contexto |
| 6 | `search_fred_series_related_tags` | Tags relacionados en búsqueda | Texto + tags | Tags relacionados contextuales |
| 7 | `get_fred_series_tags` | Tags de una serie específica | Series ID | Tags de esa serie |

#### 📊 **Categoría 3: Datos de Series**

| # | Tool | Función | Input Principal | Output |
|---|------|---------|-----------------|--------|
| 8 | `get_fred_series_observations` | Obtener datos históricos | Series ID | Observaciones (valores+fechas) |

#### 📁 **Categoría 4: Navegación de Categorías**

| # | Tool | Función | Input Principal | Output |
|---|------|---------|-----------------|--------|
| 9 | `get_fred_category` | Info de una categoría | Category ID | Nombre, parent_id, notas |
| 10 | `get_fred_category_children` | Subcategorías | Category ID | Lista de hijos directos |
| 11 | `get_fred_category_related` | Categorías relacionadas | Category ID | Categorías relacionadas |
| 12 | `get_fred_category_series` | Series en categoría | Category ID | Series de esa categoría |
| 13 | `get_fred_category_tags` | Tags en categoría | Category ID | Tags usados en esa categoría |
| 14 | `get_fred_category_related_tags` | Tags relacionados en categoría | Category ID + tags | Tags relacionados en contexto |

#### 🩺 **Categoría 5: Operaciones y Salud del Sistema**

| # | Tool | Función | Input Principal | Output |
|---|------|---------|-----------------|--------|
| 15 | `system_health` | Telemetría y estado operativo | Ninguno | Resumen de cache, rate limiter y métricas |

### Versiones y Disponibilidad

| Tool | Añadida en Versión | Estado |
|------|-------------------|--------|
| 1-3 | v0.1.1-v0.1.3 | ✅ Estable |
| 4 | v0.1.4 | ✅ Estable |
| 5 | v0.1.5 | ✅ Estable |
| 6 | v0.1.6 | ✅ Estable |
| 7-10 | v0.1.7 | ✅ Estable |
| 11-14 | v0.1.8 | ✅ Estable |
| 15 | v0.1.9 | ✅ Estable (Actual) |

---

## 4. Cómo Funcionan las Herramientas

### Anatomía de una Herramienta

Todas las tools siguen el mismo patrón:

```python
def nombre_tool(
    parametro_requerido: tipo,
    parametro_opcional: Optional[tipo] = valor_default,
    ...
) -> str:  # Siempre retornan JSON string
    """
    Docstring con descripción completa.
    
    Args:
        parametro_requerido: Descripción
        parametro_opcional: Descripción
    
    Returns:
        JSON string con estructura estandarizada
    
    Examples:
        >>> nombre_tool("valor")
    """
    # 1. Validación de entrada
    # 2. Llamada a FRED API
    # 3. Procesamiento de respuesta
    # 4. Formato JSON estandarizado
    # 5. Manejo de errores
```

### Estructura de Respuesta Estándar

Todas las tools retornan JSON con esta estructura:

```json
{
  "tool": "nombre_de_la_tool",
  "data": [
    // Datos principales (array o object)
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "total_count": 100,
    "returned_count": 20,
    // ... más metadata específica de la tool
  }
}
```

### Manejo de Errores

```json
{
  "tool": "nombre_de_la_tool",
  "error": "Descripción del error",
  "input_parameters": {
    // Parámetros que causaron el error
  }
}
```

### Conceptos FRED Importantes

#### Tags
- **Etiquetas** que categorizan series
- **7 grupos de tags**:
  - `freq`: Frecuencia (monthly, quarterly, annual, etc.)
  - `gen`: General/concepto (gdp, inflation, unemployment, etc.)
  - `geo`: Geografía (usa, california, texas, etc.)
  - `geot`: Tipo geográfico (nation, state, county, msa)
  - `rls`: Release (publicación de datos)
  - `seas`: Ajuste estacional (sa=seasonally adjusted, nsa=not seasonally adjusted)
  - `src`: Fuente (bls, bea, census, frb, etc.)

#### Categorías
- Organización **jerárquica** de series
- **8,000+ categorías** en FRED
- Ejemplo: `0` (root) → `10` (Employment & Population) → `12` (Unemployment)

#### Series
- **Serie temporal** de datos económicos
- Identificada por **Series ID** (ej: "GDP", "UNRATE", "CPIAUCSL")
- Contiene: observaciones (fechas + valores), metadata, tags, categoría

---

## 5. Generando Prompts de Prueba Individual

### Template General de Prompt Individual

```
Usa la herramienta [NOMBRE_TOOL] para [OBJETIVO_CLARO].

Parámetros:
- [parametro1]: [valor]
- [parametro2]: [valor]

Espero que el resultado [DESCRIPCIÓN_RESULTADO_ESPERADO].
```

### Ejemplos por Herramienta

#### Tool 1: `search_fred_series` (Búsqueda de Series)

**Prompt Básico:**
```
Busca series económicas relacionadas con "desempleo" en FRED.
```

**Prompt Avanzado:**
```
Busca series de desempleo que cumplan:
- Contengan "unemployment rate" en el título
- Sean de frecuencia mensual
- Estén ajustadas estacionalmente
- Limitar a 10 resultados más relevantes
```

**Prompt con Filtros:**
```
Busca series del PIB (GDP) que:
- Tengan frecuencia "Quarterly"
- Incluyan los tags "usa" y "sa" (semicolon-delimited: "usa;sa")
- Ordena por última actualización (descendente)
- Máximo 15 resultados
```

---

#### Tool 2: `get_fred_tags` (Descubrir Tags)

**Prompt Básico:**
```
Muéstrame todos los tags de frecuencia disponibles en FRED.
```

**Prompt Avanzado:**
```
Obtén los tags de tipo "source" (fuente de datos) ordenados por popularidad,
mostrando los 20 más importantes.
```

**Prompt para Búsqueda:**
```
Busca tags que contengan la palabra "inflation" en su nombre o descripción.
```

---

#### Tool 3: `search_fred_related_tags` (Tags Relacionados)

**Prompt Básico:**
```
Encuentra tags relacionados con "gdp" en FRED.
```

**Prompt Avanzado:**
```
Encuentra tags relacionados con "usa" y "monthly" que:
- Sean del grupo "geo" (geografía)
- Excluyan tags de series discontinuadas
- Ordena por cantidad de series que usan esos tags
```

---

#### Tool 4: `get_fred_series_by_tags` (Series por Tags)

**Prompt Básico:**
```
Encuentra series que tengan los tags "usa", "monthly" y "nsa" (todos requeridos).
```

**Prompt con Exclusión:**
```
Busca series de empleo que:
- DEBEN tener: "usa", "monthly", "employment"
- NO DEBEN tener: "discontinued", "revision"
- Ordena por popularidad, máximo 20 series
```

---

#### Tool 7: `get_fred_series_tags` (Tags de una Serie)

**Prompt Básico:**
```
¿Qué tags tiene la serie "UNRATE" (tasa de desempleo)?
```

**Prompt Analítico:**
```
Obtén todos los tags de la serie "GDP" y ordénalos por popularidad
para entender cómo está categorizada.
```

---

#### Tool 8: `get_fred_series_observations` (Datos Históricos)

**Prompt Básico:**
```
Obtén los datos históricos del PIB (serie "GDP").
```

**Prompt con Rango de Fechas:**
```
Dame las observaciones de la tasa de desempleo (UNRATE) desde 
2020-01-01 hasta 2024-12-31.
```

**Prompt con Transformación:**
```
Obtén el CPI (CPIAUCSL) transformado a tasa de inflación año a año 
(units="pc1") para los últimos 24 meses.
```

**Prompt con Agregación:**
```
Convierte la tasa de fondos federales diaria (DFF) a promedio mensual
usando agregación por promedio.
```

---

#### Tool 9-10: Categorías Básicas

**Prompt para Info de Categoría:**
```
¿Cuál es el nombre y descripción de la categoría 125 (Trade Balance)?
```

**Prompt para Subcategorías:**
```
Muéstrame todas las subcategorías directas de "International Data" (categoría 13).
```

---

#### Tool 11: `get_fred_category_related` (Categorías Relacionadas)

**Prompt Básico:**
```
¿Qué categorías están relacionadas con "Employment & Population" (categoría 10)?
```

**Prompt para Exploración:**
```
Quiero explorar categorías relacionadas con "National Accounts" (categoría 32992)
para descubrir otros tipos de datos macroeconómicos disponibles.
```

---

#### Tool 12: `get_fred_category_series` (Series en Categoría)

**Prompt Básico:**
```
Lista las 10 series más populares en la categoría "Trade Balance" (125).
```

**Prompt Filtrado:**
```
Obtén series en la categoría de "Unemployment" (12) que:
- Tengan tags "usa" y "monthly"
- Sean las 20 actualizadas más recientemente
```

---

#### Tool 13: `get_fred_category_tags` (Tags en Categoría)

**Prompt Básico:**
```
¿Qué tags se usan en series de la categoría "Trade Balance" (125)?
```

**Prompt por Grupo:**
```
Muéstrame solo los tags de frecuencia usados en la categoría 
"Employment & Population" (10), ordenados por cantidad de series.
```

**Prompt de Búsqueda:**
```
En la categoría de "Money, Banking & Finance" (32991), busca tags
que contengan "interest" o "rate".
```

---

#### Tool 14: `get_fred_category_related_tags` (Tags Relacionados en Categoría)

**Prompt Básico:**
```
En la categoría de "National Accounts" (32992), ¿qué tags aparecen
junto con "quarterly"?
```

**Prompt con AND/NOT:**
```
En categoría 125:
- Busca tags que aparecen con "usa" Y "quarterly" (ambos requeridos)
- Pero excluye tags relacionados con "annual"
- Solo muestra tags del grupo "src" (fuente)
```

---

#### Tool 15: `system_health` (Salud Operativa)

**Prompt Básico:**
```
Ejecuta la tool `system_health` y devuelve el resultado tal cual.
```

**Prompt de Diagnóstico:**
```
Consulta `system_health` y verifica:
- ¿Qué backend de caché está activo?
- ¿Hay penalizaciones activas en el rate limiter?
- ¿Cuál es la latencia p95 reportada por el cliente FRED?
```

**Tips de prueba:**
- Útil como "heartbeat" en pipelines automatizados antes de ejecutar workflows más costosos.
- Permite validar que Redis o DiskCache están conectados antes de realizar cargas masivas.
- Exponer el resultado a tus dashboards ayuda a detectar cambios en tasa de aciertos de caché o reintentos.

---

## 6. Diseñando Workflows Multi-Herramienta

### Principios de Diseño de Workflows

1. **Secuencialidad**: Una tool provee información para la siguiente
2. **Refinamiento Progresivo**: Empezar amplio, ir estrechando
3. **Validación**: Verificar antes de obtener datos grandes
4. **Contexto**: Cada paso agrega contexto para el siguiente

### Patrones de Workflow Comunes

#### Patrón 1: Descubrimiento → Filtrado → Datos

```
1. Buscar series relevantes (search_fred_series)
   ↓
2. Analizar tags de series encontradas (get_fred_series_tags)
   ↓
3. Refinar búsqueda con tags (get_fred_series_by_tags)
   ↓
4. Obtener observaciones (get_fred_series_observations)
```

#### Patrón 2: Tag Discovery → Series Discovery → Data

```
1. Descubrir tags disponibles (get_fred_tags)
   ↓
2. Encontrar tags relacionados (search_fred_related_tags)
   ↓
3. Buscar series con esos tags (get_fred_series_by_tags)
   ↓
4. Obtener datos (get_fred_series_observations)
```

#### Patrón 3: Category Navigation → Series → Data

```
1. Explorar categoría (get_fred_category)
   ↓
2. Ver subcategorías (get_fred_category_children)
   ↓
3. Listar series en categoría (get_fred_category_series)
   ↓
4. Obtener observaciones (get_fred_series_observations)
```

#### Patrón 4: Context-Aware Tag Discovery

```
1. Buscar series (search_fred_series)
   ↓
2. Ver tags en esos resultados (search_fred_series_tags)
   ↓
3. Descubrir tags relacionados en ese contexto (search_fred_series_related_tags)
   ↓
4. Refinar con nuevos tags (search_fred_series con más tags)
```

---

## 7. Ejemplos de Workflows Completos

### Workflow 1: Análisis Completo de Desempleo USA

**Objetivo:** Obtener datos de desempleo USA, ajustados estacionalmente, con contexto completo.

**Prompt del Workflow:**
```
Necesito analizar datos de desempleo en USA. Por favor:

1. Busca series de desempleo que contengan "unemployment rate"
   - Limita a 20 resultados
   - Ordena por popularidad

2. Para la serie más popular encontrada:
   - Obtén sus tags para entender sus características
   - Verifica que sea mensual, USA, y ajustada estacionalmente

3. Usa esos tags para buscar series similares:
   - Busca series con tags "usa", "monthly", "sa", "unemployment"
   - Excluye series descontinuadas

4. Para las 3 series principales:
   - Obtén observaciones desde 2020-01-01 hasta hoy
   - Ordena por fecha descendente

5. Resume las características de los datos obtenidos.
```

**Desglose de Tools Usadas:**
```
Tool 1: search_fred_series("unemployment rate", limit=20, order_by="popularity")
Tool 2: get_fred_series_tags([series_id más popular])
Tool 3: get_fred_series_by_tags("usa;monthly;sa;unemployment", exclude_tag_names="discontinued", limit=3)
Tool 4: get_fred_series_observations([series_id_1], observation_start="2020-01-01")
Tool 4: get_fred_series_observations([series_id_2], observation_start="2020-01-01")
Tool 4: get_fred_series_observations([series_id_3], observation_start="2020-01-01")
```

---

### Workflow 2: Exploración de Categorías de Comercio

**Objetivo:** Navegar categorías de comercio internacional y obtener series relevantes.

**Prompt del Workflow:**
```
Quiero explorar datos de comercio internacional en FRED:

1. Obtén información de la categoría "International Data" (ID: 13)

2. Lista todas sus subcategorías para ver qué tipos de datos hay

3. Para la subcategoría "Trade Balance" (ID: 125):
   - ¿Qué tags se usan en series de esta categoría?
   - Filtra solo tags de frecuencia
   
4. Obtén las 10 series más populares de esta categoría
   - Que sean mensuales (tag: "monthly")
   - Ordenadas por popularidad

5. Para la serie #1 más popular:
   - Obtén los últimos 36 meses de datos
   - Ordena cronológicamente (más reciente primero)
```

**Desglose de Tools:**
```
Tool 1: get_fred_category(13)
Tool 2: get_fred_category_children(13)
Tool 3: get_fred_category_tags(125, tag_group_id="freq")
Tool 4: get_fred_category_series(125, tag_names="monthly", order_by="popularity", limit=10)
Tool 5: get_fred_series_observations([top_series_id], limit=36, sort_order="desc")
```

---

### Workflow 3: Descubrimiento Progresivo de Inflación

**Objetivo:** Descubrir y analizar series de inflación usando tags.

**Prompt del Workflow:**
```
Necesito encontrar datos de inflación en USA:

1. Descubre qué tags existen relacionados con "inflation"
   - Busca en todos los grupos de tags
   - Limita a 30 resultados más relevantes

2. De esos tags, encuentra cuáles están relacionados con "usa" y "monthly"
   - Excluye tags de series discontinuadas

3. Con los tags más relevantes encontrados:
   - Busca series que tengan "cpi" O "inflation" en el título
   - Y que tengan los tags "usa", "monthly", "sa"
   - Máximo 10 series más populares

4. Para las top 3 series:
   - Obtén datos desde 2015-01-01
   - Transforma a tasa de inflación año-a-año (units="pc1")

5. Compara las características de las 3 series obtenidas.
```

**Desglose de Tools:**
```
Tool 1: get_fred_tags(search_text="inflation", limit=30, order_by="popularity")
Tool 2: search_fred_related_tags("usa;monthly", exclude_tag_names="discontinued")
Tool 3: search_fred_series("cpi inflation", tag_names="usa;monthly;sa", limit=10)
Tool 4: get_fred_series_observations([series_1], observation_start="2015-01-01", units="pc1")
Tool 4: get_fred_series_observations([series_2], observation_start="2015-01-01", units="pc1")
Tool 4: get_fred_series_observations([series_3], observation_start="2015-01-01", units="pc1")
```

---

### Workflow 4: Comparación Multi-Fuente

**Objetivo:** Comparar datos de desempleo de diferentes fuentes (BLS vs OECD).

**Prompt del Workflow:**
```
Compara datos de desempleo de diferentes fuentes:

1. Busca series de "unemployment rate" que sean de USA, mensuales, SA

2. Agrupa los resultados por fuente (tag src):
   - Identifica qué fuentes proveen estos datos
   - Usa search_series_tags para descubrir sources

3. Para cada fuente identificada (ej: bls, oecd):
   - Busca series específicas con ese tag de fuente
   - Obtén la serie más popular de cada fuente

4. Para cada serie encontrada:
   - Obtén datos desde 2019-01-01 hasta hoy
   - Compara valores y frecuencias

5. Resume diferencias entre fuentes.
```

**Desglose de Tools:**
```
Tool 1: search_fred_series("unemployment rate", tag_names="usa;monthly;sa", limit=20)
Tool 2: search_fred_series_tags("unemployment rate", "usa;monthly;sa", tag_group_id="src")
Tool 3: get_fred_series_by_tags("usa;monthly;sa;bls", order_by="popularity", limit=1)
Tool 3: get_fred_series_by_tags("usa;monthly;sa;oecd", order_by="popularity", limit=1)
Tool 4: get_fred_series_observations([bls_series], observation_start="2019-01-01")
Tool 4: get_fred_series_observations([oecd_series], observation_start="2019-01-01")
```

---

### Workflow 5: Análisis Regional de Empleo

**Objetivo:** Comparar datos de empleo a nivel nacional vs estados.

**Prompt del Workflow:**
```
Análisis de empleo nacional y por estados:

1. Busca series de "employment" con tag "usa" y "monthly"

2. En esos resultados, descubre:
   - ¿Qué tags geográficos existen? (tag_group_id="geo")
   - ¿Qué tipos geográficos hay? (tag_group_id="geot")

3. Obtén series de nivel nacional:
   - Tags: "usa", "monthly", "sa", "nation"
   - Top 5 por popularidad

4. Obtén series de nivel estatal:
   - Tags: "monthly", "sa", "state"
   - Estados específicos: california, texas, new york
   - 1 serie por estado

5. Para cada serie (nacional + 3 estados):
   - Obtén datos desde 2020-01-01
   - Calcula variación porcentual (units="pch")

6. Compara tendencias entre niveles geográficos.
```

**Desglose de Tools:**
```
Tool 1: search_fred_series("employment", tag_names="usa;monthly", limit=30)
Tool 2: search_fred_series_tags("employment", "usa;monthly", tag_group_id="geo")
Tool 2: search_fred_series_tags("employment", "usa;monthly", tag_group_id="geot")
Tool 3: get_fred_series_by_tags("usa;monthly;sa;nation;employment", limit=5, order_by="popularity")
Tool 4: get_fred_series_by_tags("monthly;sa;state;california;employment", limit=1)
Tool 4: get_fred_series_by_tags("monthly;sa;state;texas;employment", limit=1)
Tool 4: get_fred_series_by_tags("monthly;sa;state;new york;employment", limit=1)
Tool 5: get_fred_series_observations([national_series], observation_start="2020-01-01", units="pch")
[Repetir Tool 5 para cada serie estatal]
```

---

## 8. Patrones Comunes de Uso

### Patrón: Validación Antes de Descarga

**Problema:** No queremos descargar datos masivos sin saber si son lo que necesitamos.

**Solución:**
```
1. Buscar serie (search_fred_series)
2. Verificar tags (get_fred_series_tags)
3. Confirmar características
4. ENTONCES descargar datos (get_fred_series_observations)
```

**Ejemplo de Prompt:**
```
Antes de descargar datos del PIB:
1. Busca series de "GDP" 
2. Para la primera, verifica sus tags
3. Confirma que sea quarterly y seasonally adjusted
4. Solo si cumple, descarga datos desde 2010
```

---

### Patrón: Descubrimiento Iterativo

**Problema:** No sabemos exactamente qué existe, necesitamos explorar.

**Solución:**
```
1. Búsqueda amplia
2. Analizar resultados (tags, categorías)
3. Refinar búsqueda con lo aprendido
4. Repetir hasta encontrar lo exacto
```

**Ejemplo de Prompt:**
```
Quiero datos de confianza del consumidor, pero no sé qué existe:

1. Busca "consumer confidence" ampliamente (50 resultados)
2. Analiza tags comunes en resultados (search_series_tags)
3. Busca tags relacionados interesantes (search_related_tags)
4. Refina búsqueda con los mejores tags encontrados
5. Descarga datos de las series más relevantes
```

---

### Patrón: Comparación Cross-Category

**Problema:** Necesitamos datos de diferentes categorías para análisis conjunto.

**Solución:**
```
1. Identificar categorías relevantes (category navigation)
2. Para cada categoría, extraer series clave
3. Estandarizar datos (mismas fechas, transformaciones)
4. Comparar
```

**Ejemplo de Prompt:**
```
Compara datos de empleo vs producción industrial:

1. Categoría Employment (10): obtén top serie de unemployment
2. Categoría Production (1): obtén top serie de industrial production
3. Para ambas:
   - Datos desde 2015-01-01
   - Frecuencia mensual
   - Transforma a variación porcentual año-a-año (units="pc1")
4. Analiza correlación
```

---

### Patrón: Tag-Based Filtering Pipeline

**Problema:** Queries muy complejas con múltiples condiciones.

**Solución:**
```
1. Identificar todos los tags necesarios (get_tags, related_tags)
2. Validar que existen series con ESA combinación (series_by_tags con limit=1)
3. Si existe, hacer búsqueda completa
4. Si no, ajustar tags
```

**Ejemplo de Prompt:**
```
Necesito series muy específicas:
- Datos mensuales de inflación
- No ajustadas estacionalmente
- Solo de la fuente BLS
- Excluyendo series descontinuadas

1. Verifica que esa combinación existe:
   get_series_by_tags("monthly;nsa;bls;inflation", 
                      exclude="discontinued", limit=1)
   
2. Si existe (count > 0):
   - Obtén todas las series (limit=50)
   - Ordena por popularidad
   
3. Si NO existe:
   - Relaja un criterio (ej: permitir sa también)
   - Reintenta
```

---

## 9. Mejores Prácticas

### Para Prompts Individuales

1. **Sé Específico con Parámetros:**
   ```
   ❌ Malo: "Busca GDP"
   ✅ Bueno: "Busca series de GDP con frecuencia quarterly, USA, SA, últimos 10 años"
   ```

2. **Usa Límites Apropiados:**
   ```
   - Exploración: limit=50-100
   - Refinado: limit=10-20
   - Final: limit=1-5
   ```

3. **Especifica Ordenamiento:**
   ```
   - Para relevancia: order_by="popularity" o "search_rank"
   - Para actualidad: order_by="last_updated"
   - Para alfabético: order_by="title"
   ```

4. **Usa Tags Correctamente:**
   ```
   ✅ Correcto: tag_names="usa;monthly;sa" (semicolon-delimited)
   ❌ Incorrecto: tag_names="usa, monthly, sa" (commas no funcionan)
   ```

---

### Para Workflows

1. **Empezar Amplio, Luego Refinar:**
   ```
   Paso 1: Búsqueda amplia (limit=50)
   Paso 2: Analizar resultados
   Paso 3: Búsqueda refinada (limit=10)
   Paso 4: Obtener datos (series específicas)
   ```

2. **Validar en Cada Paso:**
   ```
   - Verifica que cada step retorna datos
   - Chequea counts en metadata
   - Confirma tags/categorías antes de siguiente paso
   ```

3. **Manejar Casos Edge:**
   ```
   - ¿Qué pasa si la búsqueda retorna 0 resultados?
   - ¿Qué hacer si una serie no tiene datos para el rango pedido?
   - Plan B si los tags no existen
   ```

4. **Documentar el Workflow:**
   ```
   Para cada paso, explica:
   - Qué tool usas
   - Por qué (objetivo)
   - Qué esperas obtener
   - Cómo usarás el resultado en el siguiente paso
   ```

---

### Para Optimización

1. **Minimizar Llamadas:**
   ```
   ❌ Malo: 
   - get_series_observations para 50 series (50 llamadas)
   
   ✅ Bueno:
   - Filtrar a top 5 primero (1 llamada)
   - Luego get_observations solo de esas 5 (5 llamadas)
   ```

2. **Usar Filtros en la Fuente:**
   ```
   ❌ Malo: Obtener 1000 series y filtrar localmente
   ✅ Bueno: Usar tag_names, exclude_tag_names, filter_variable desde el inicio
   ```

3. **Aprovechar Metadata:**
   ```
   - Revisa total_count antes de pedir más datos
   - Usa returned_count para saber si hay más páginas
   - Chequea realtime_start/end para contexto temporal
   ```

---

### Para Debugging

1. **Empezar Simple:**
   ```
   1. Probar tool individualmente sin filtros
   2. Añadir filtros uno a uno
   3. Identificar cuál falla
   ```

2. **Revisar Documentación API:**
   ```
   Cada tool tiene su referencia en docs/api/
   - FRED_SEARCH_REFERENCE.md
   - FRED_TAGS_REFERENCE.MD
   - etc.
   ```

3. **Verificar Formato de Parámetros:**
   ```
   - Dates: "YYYY-MM-DD"
   - Tags: "tag1;tag2;tag3" (semicolons!)
   - IDs: integers, not strings
   - Enums: valores exactos (case-sensitive)
   ```

---

## 10. Troubleshooting

### Problemas Comunes y Soluciones

#### Problema 1: "No results found" (0 series)

**Causas Posibles:**
- Tags incorrectos o inexistentes
- Filtros demasiado restrictivos
- Typo en series_id

**Solución:**
```
1. Verifica tags existen:
   get_fred_tags(search_text="tu_tag")

2. Relaja filtros gradualmente:
   - Quita exclude_tag_names
   - Usa menos tags en tag_names
   - Quita filter_variable/filter_value

3. Prueba búsqueda más amplia:
   search_fred_series("término general", limit=100)
```

**Ejemplo:**
```
❌ Problema:
get_series_by_tags("usa;monthly;sa;unemployment;california", limit=10)
# Returns: 0 series

✅ Solución:
# Paso 1: Verificar que tags existen
get_fred_tags(search_text="california")

# Paso 2: Probar con menos tags
get_series_by_tags("monthly;sa;california", limit=10)

# Paso 3: Revisar resultados y refinar
```

---

#### Problema 2: "Rate limit exceeded"

**Causa:**
- Demasiadas llamadas en poco tiempo
- FRED API tiene límite de 120 requests/minuto

**Solución:**
```
1. Espera 60 segundos
2. El sistema tiene retry automático (3 intentos)
3. Reduce frecuencia de llamadas
4. Usa limit para obtener menos datos por llamada
```

---

#### Problema 3: "Invalid parameter format"

**Causas:**
- Tags con commas en vez de semicolons
- Fechas en formato incorrecto
- Enum value inválido

**Solución:**
```
✅ Formato Correcto:
- Tags: "usa;monthly;sa" (semicolons!)
- Fechas: "2020-01-01" (YYYY-MM-DD)
- Order by: "popularity" (lowercase, exact match)
- Tag group: "freq" (no "frequency")

❌ Formatos Incorrectos:
- Tags: "usa, monthly, sa" (commas)
- Fechas: "01-01-2020" (wrong format)
- Order by: "Popularity" (case mismatch)
```

---

#### Problema 4: "Series has no observations"

**Causa:**
- Serie válida pero sin datos para el rango pedido
- Serie discontinuada

**Solución:**
```
1. Verifica tags de la serie:
   get_series_tags([series_id])
   # Busca tag "discontinued"

2. Prueba sin fechas (obtener todo):
   get_series_observations([series_id])

3. Ajusta rango de fechas:
   # En metadata viene observation_start/observation_end
```

---

#### Problema 5: Workflow complejo falla a mitad

**Causa:**
- Un paso intermedio retorna 0 resultados
- Dependencia entre steps no manejada

**Solución:**
```
1. Ejecuta cada step individualmente primero
2. Verifica metadata.total_count de cada step
3. Agrega validación entre steps:

Ejemplo:
Step 1: Buscar series
Step 2: IF step1.metadata.total_count > 0:
           Obtener tags
        ELSE:
           Ajustar búsqueda y reintentar Step 1
Step 3: IF step2.data.length > 0:
           Usar esos tags
        ELSE:
           Usar tags por defecto
```

---

### Checklist de Verificación

Antes de ejecutar un workflow complejo:

- [ ] Cada tool usada existe y está disponible (ver sección 3)
- [ ] Parámetros requeridos están presentes
- [ ] Formato de parámetros es correcto (tags con `;`, fechas `YYYY-MM-DD`)
- [ ] Límites son razonables (no pedir 10,000 series)
- [ ] Hay plan B si algún step falla
- [ ] Orden de steps tiene sentido (no necesitas datos de Step 3 para Step 1)
- [ ] Documentaste qué hace cada step
- [ ] Probaste steps individuales primero

---

## Recursos Adicionales

### Documentación del Proyecto

- **Architecture**: `docs/architecture.md` - Entender estructura del proyecto
- **API References**: `docs/api/` - Documentación detallada de cada tool
- **Changelog**: `docs/Changelog/CHANGELOG.md` - Historial de cambios
- **Release Notes**: `docs/Release_notes/` - Notas de cada versión

### Documentación Externa

- **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastMCP Framework**: https://github.com/jlowin/fastmcp

### Comandos Útiles

```bash
# Ver versión actual
python -c "from trabajo_ia_server import __version__; print(__version__)"

# Ejecutar servidor
python -m trabajo_ia_server

# Con UV
uv run python -m trabajo_ia_server

# Ejecutar tests
pytest tests/

# Ver logs
# Los logs se imprimen a stdout por defecto
```

---

## Conclusión

Esta guía te proporciona:

✅ **Comprensión completa** del proyecto MCP Trabajo IA Server  
✅ **14 herramientas FRED + 1 herramienta de salud** clasificadas y explicadas
✅ **Templates de prompts** para pruebas individuales  
✅ **5 workflows completos** listos para usar  
✅ **Patrones de diseño** para crear tus propios workflows  
✅ **Mejores prácticas** para optimizar pruebas  
✅ **Troubleshooting** para resolver problemas comunes  

### Próximos Pasos

1. **Lee la documentación de arquitectura** (`docs/architecture.md`)
2. **Explora las referencias API** de las tools que más usarás (`docs/api/`)
3. **Prueba prompts individuales** para familiarizarte
4. **Experimenta con workflows simples** (2-3 tools)
5. **Diseña workflows complejos** usando los patrones aprendidos

### Feedback y Contribuciones

Esta guía es un documento vivo. Si encuentras:
- Casos de uso no cubiertos
- Errores o mejoras
- Nuevos patrones útiles

Por favor documenta y comparte para futuras versiones.

---

**Versión:** 1.0  
**Última actualización:** 2025-11-01  
**Mantenido por:** Equipo Trabajo IA MCP Server
