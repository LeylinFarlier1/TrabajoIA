# Trabajo IA - MCP Server for FRED Economic Data

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.20.0-green.svg)](https://modelcontextprotocol.io/)
[![Status](https://img.shields.io/badge/status-ready-brightgreen.svg)]()

Servidor MCP (Model Context Protocol) completamente funcional que proporciona acceso a datos económicos de la Reserva Federal (FRED) a través de GitHub Copilot y otros clientes MCP.

## 🚀 Estado: LISTO PARA USAR

✅ **Instalación completa**  
✅ **Configuración de VS Code lista**  
✅ **API Key configurada**  
✅ **Servidor probado y funcionando**

## 📖 Inicio Rápido

1. **Configura tu API Key de FRED** (gratis en fred.stlouisfed.org)
2. **Instala el servidor**: `cd server && uv pip install -e .`
3. **Configura tu cliente** (Claude Desktop, VSCode, o Claude Code)
4. **Reinicia tu cliente** completamente
5. **¡Empieza a preguntar!**: `Busca series sobre desempleo en Estados Unidos`

📘 **[Ver Guía Completa de Instalación →](./QUICKSTART.md)**

## 📁 Estructura del Proyecto

```
trabajoIA/
├── server/                       # Servidor MCP (Python 3.10+)
│   ├── src/trabajo_ia_server/
│   │   ├── server.py             # FastMCP server + tool registration
│   │   ├── config.py             # Configuración centralizada
│   │   │
│   │   ├── tools/                # Herramientas MCP (12 tools)
│   │   │   ├── fred/             # FRED API tools (11 herramientas)
│   │   │   ├── system/           # health.py - Internal monitoring (not exposed)
│   │   │   └── workflows/        # Tool wrappers
│   │   │
│   │   ├── workflows/            # Análisis complejos multi-paso
│   │   │   ├── analyze_gdp.py    # GDP cross-country orchestrator
│   │   │   ├── layers/           # 3-layer architecture
│   │   │   │   ├── fetch_data.py      # FRED data retrieval
│   │   │   │   ├── analyze_data.py    # Economic analysis
│   │   │   │   └── format_output.py   # Output formatting
│   │   │   └── utils/            # GDP mappings & validators
│   │   │
│   │   └── utils/                # Utilidades compartidas
│   │       ├── cache.py          # Multi-backend caching
│   │       ├── rate_limiter.py   # FRED API rate limiting
│   │       ├── metrics.py        # Prometheus-style telemetry
│   │       ├── fred_client.py    # Unified FRED client
│   │       └── logger.py         # Structured logging
│   │
│   ├── tests/                    # Suite de pruebas (pytest)
│   │   ├── unit/                 # Tests unitarios
│   │   ├── integration/          # Tests de integración
│   │   └── fixtures/             # Datos de prueba
│   │
│   ├── docs/                     # Documentación técnica
│   │   ├── api/                  # Referencias FRED API
│   │   ├── workflows/            # Docs de workflows
│   │   ├── guides/               # Guías de desarrollo
│   │   ├── Release_notes/        # Notas de versión
│   │   └── architecture.md       # Arquitectura del sistema
│   │
│   ├── .env                      # Variables de entorno (API keys)
│   └── pyproject.toml            # Dependencias y configuración
│
├── prueba_workflow/              # Ejemplo: Análisis GDP G7 1980-2010
│   ├── *.png                     # 7 visualizaciones generadas
│   ├── analysis_results.json     # Resultados completos del análisis
│   ├── gdp_data_raw.csv          # Dataset en formato tidy
│   └── README.md                 # Documentación del análisis
│
├── prueba_modular/               # Ejemplo: Análisis modular paso a paso
│   ├── gdp_analysis.py           # Script de análisis principal
│   └── README.md                 # Metodología y hallazgos
│
├── correcion_workflow/           # Detección de quiebres estructurales
│   ├── create_structural_breaks_timeline.py
│   ├── 6_structural_breaks_50pct.png
│   └── structural_breaks_timeline.json
│
├── mcp.json                      # Configuración MCP para VS Code
└── README.md                     # Este archivo
```

## 🛠️ Características

### v0.1.9 - Última Versión
- **Caché Inteligente**: Respuestas rápidas (<400ms) con caché multi-nivel
- **Rate Limiting**: Gestión automática de límites de FRED API
- **Telemetría**: Métricas y logging estructurado
- **12 Herramientas MCP**: 11 FRED tools + 1 GDP workflow
- **GDP Cross-Country Analysis**: Análisis económico completo con:
  - 238 países/territorios + presets (G7, G20, BRICS, LATAM, etc.)
  - Detección de quiebres estructurales (rolling variance method)
  - Análisis de convergencia (sigma/beta)
  - Métricas de crecimiento (CAGR, volatilidad, estabilidad)
  - Rankings y comparaciones multi-país
- **System Health**: Monitoreo del estado del servidor

## 📊 Herramientas Disponibles

### Herramientas Core FRED
| Herramienta | Descripción |
|-------------|-------------|
| `search_fred_series` | Buscar series económicas con filtros avanzados |
| `get_fred_series_observations` | Obtener datos históricos de series |
| `get_fred_tags` | Listar todos los tags disponibles |
| `search_fred_related_tags` | Encontrar tags relacionados |
| `get_fred_series_by_tags` | Buscar series por combinación de tags |
| `search_fred_series_tags` | Tags para búsquedas de series |
| `search_fred_series_related_tags` | Tags relacionados en búsquedas |
| `get_fred_series_tags` | Obtener tags de serie específica |

### Herramientas de Categorías
| Herramienta | Descripción |
|-------------|-------------|
| `get_fred_category` | Información de categoría específica |
| `get_fred_category_children` | Sub-categorías de una categoría |
| `get_fred_category_series` | Series en una categoría |

### Workflows Avanzados
| Herramienta | Descripción |
|-------------|-------------|
| `analyze_gdp_cross_country` | Análisis GDP multi-país completo con quiebres estructurales |

### Sistema
| Herramienta | Descripción |
|-------------|-------------|
| `system_health` | Estado del servidor, caché y métricas |

## 🔧 Configuración Actual

**VS Code MCP Config:**
```
C:\Users\agust\AppData\Roaming\Code\User\globalStorage\github.copilot\mcp-config.json
```

**Configuración activa:**
- Caché: Memoria (TTL 300s)
- Rate Limit: 120 req/min
- Métricas: Habilitadas (JSON)
- Logging: INFO

## 💻 Desarrollo

### Ejecutar Tests
```bash
cd server
pytest tests/
```

### Ejecutar Servidor Manualmente
```bash
cd server
python -m trabajo_ia_server.server
```

### Ver Logs
```bash
# Los logs se muestran en la consola durante la ejecución
# También están disponibles en VS Code Developer Tools
```

## 📚 Documentación

### Inicio Rápido
- **[Quick Start Guide](./QUICKSTART.md)** - Instalación paso a paso para Claude Desktop, VSCode y Claude Code
- **[Server README](./server/README.md)** - Documentación técnica del servidor
- **[Architecture](./server/docs/architecture.md)** - Entender la arquitectura del sistema

### Referencia Técnica
- **[GDP Workflow Reference](./server/docs/workflows/ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md)** - Documentación completa del análisis GDP
- **[API Reference](./server/docs/api/)** - Referencia detallada de APIs FRED (11 documentos)
- **[Working Paper](./server/docs/WORKING_PAPER_MCP_ARCHITECTURE.md)** - Diseño arquitectónico MCP

### Versiones y Cambios
- **[Release Notes v0.1.9](./server/docs/Release_notes/RELEASE_NOTES_v0.1.9.md)** - Cache, telemetría, resilience
- **[CHANGELOG](./server/docs/Changelog/CHANGELOG.md)** - Historial completo de cambios
- **[v0.2.0 Expansion Plan](./server/docs/planning/v0.2.0_expansion_plan.md)** - Roadmap futuro

### Guías de Desarrollo
- **[Testing Guide](./server/docs/guides/MCP_PROJECT_TESTING_GUIDE.md)** - Cómo escribir tests
- **[New Tool Guide](./server/docs/guides/IMPLEMENTACION_NUEVA_TOOL_GUIA.md)** - Implementar nuevas herramientas
- **[Version Update Guide](./server/docs/guides/VERSION_UPDATE_GUIDE.md)** - Actualizar versiones

### Ejemplos Prácticos
- **[prueba_workflow/](./prueba_workflow/)** - Análisis GDP G7 completo con 7 visualizaciones
- **[prueba_modular/](./prueba_modular/)** - Enfoque modular paso a paso
- **[correcion_workflow/](./correcion_workflow/)** - Detección de quiebres estructurales

## 🔍 Ejemplos de Uso

### Búsqueda Simple
```
@workspace Busca series sobre desempleo en Estados Unidos
```

### Datos Históricos
```
@workspace Dame los datos mensuales de GDP desde 2020 hasta hoy
```

### Análisis GDP Cross-Country
```
@workspace Analiza el GDP per cápita del G7 desde 1980 hasta 2010
@workspace Detecta quiebres estructurales en el crecimiento económico de LATAM
@workspace Compara convergencia económica entre países BRICS desde 2000
```

### Análisis de Quiebres Estructurales
El servidor implementa detección de quiebres estructurales usando **rolling variance method**:
- Ventana móvil de 5 años sobre tasas de crecimiento
- Threshold: ratio > 1.5 (aumento 50%+) o < 2/3 (reducción 33%+)
- Identifica crisis económicas y períodos de estabilización

### Exploración por Categorías
```
@workspace ¿Qué series hay disponibles en la categoría de empleo?
```

### Monitoreo
```
@workspace Muéstrame el estado del servidor MCP y sus métricas
```

## 🐛 Troubleshooting

### Servidor no responde
1. Reinicia VS Code completamente
2. Verifica que el servidor inicia: `python -m trabajo_ia_server.server`
3. Revisa Developer Tools en VS Code (Help > Toggle Developer Tools)

### Errores de API
- Verifica tu API key en `server/.env`
- Confirma conectividad a internet
- Revisa límites de tasa de FRED (120 req/min)

### Errores de Importación
```bash
cd server
pip install -e .
# o
uv sync
```

## 🤝 Contribuir

Este es un proyecto activo. Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo una licencia de código abierto.

## 🔗 Enlaces

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitHub Copilot](https://github.com/features/copilot)

## 👥 Equipo

Desarrollado por Agustin Ernesto Mealla Cormenzana.

---

**Versión:** 0.1.9  
**Última actualización:** 2 de noviembre, 2025  
**Estado:** ✅ Producción
