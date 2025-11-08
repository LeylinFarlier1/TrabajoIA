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

1. **Reinicia VS Code**
2. **Pregunta a Copilot**: `@workspace ¿Cuál es la tasa de desempleo actual?`
3. **¡Eso es todo!**

Ver [QUICKSTART.md](./QUICKSTART.md) para instrucciones detalladas.

## 📁 Estructura del Proyecto

```
trabajoIA/
├── server/                    # Código fuente del servidor MCP
│   ├── src/                   # Código principal
│   │   └── trabajo_ia_server/
│   │       ├── tools/         # Herramientas FRED y sistema
│   │       ├── utils/         # Utilidades (caché, rate limiter, métricas)
│   │       └── workflows/     # Workflows complejos
│   ├── tests/                 # Tests unitarios e integración
│   ├── docs/                  # Documentación completa
│   ├── .env                   # Variables de entorno (con tu API key)
│   └── pyproject.toml         # Configuración del proyecto
├── mcp-config.json            # Config MCP (copiado a VS Code)
├── QUICKSTART.md              # Guía de inicio rápido
└── README.md                  # Este archivo
```

## 🛠️ Características

### v0.1.9 - Última Versión
- **Caché Inteligente**: Respuestas rápidas (<400ms) con caché multi-nivel
- **Rate Limiting**: Gestión automática de límites de FRED API
- **Telemetría**: Métricas y logging estructurado
- **9 Herramientas FRED**: Búsqueda, observaciones, categorías, tags, workflows
- **System Health**: Monitoreo del estado del servidor

## 📊 Herramientas Disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `search_fred_series` | Buscar series económicas con filtros avanzados |
| `get_series_observations` | Obtener datos históricos de series |
| `fred_category_series` | Listar series por categoría |
| `fred_series_tags` | Obtener tags de una serie específica |
| `fred_tags` | Listar todos los tags disponibles |
| `fred_related_tags` | Encontrar tags relacionados |
| `fred_series_by_tags` | Buscar series por tags |
| `compare_inflation` | Comparar inflación entre regiones |
| `system_health` | Verificar estado y métricas del servidor |

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

- **[Quick Start](./QUICKSTART.md)** - Empieza aquí
- **[VS Code Integration](./server/docs/VSCODE_INTEGRATION.md)** - Guía de integración completa
- **[Server README](./server/README.md)** - Documentación del servidor
- **[Release Notes v0.1.9](./server/docs/Release_notes/RELEASE_NOTES_v0.1.9.md)** - Últimas características
- **[Architecture](./server/docs/architecture.md)** - Arquitectura del sistema
- **[API Reference](./server/docs/api/)** - Referencia de APIs FRED

## 🔍 Ejemplos de Uso

### Búsqueda Simple
```
@workspace Busca series sobre desempleo en Estados Unidos
```

### Datos Históricos
```
@workspace Dame los datos mensuales de GDP desde 2020 hasta hoy
```

### Análisis Comparativo
```
@workspace Compara la inflación entre USA, Europa y Japón en los últimos 5 años
```

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

Desarrollado por el equipo Trabajo IA.

---

**Versión:** 0.1.9  
**Última actualización:** 2 de noviembre, 2025  
**Estado:** ✅ Producción
