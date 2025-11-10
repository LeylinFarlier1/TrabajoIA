# 🚀 Quick Start Guide - FRED Economic Data MCP Server

Esta guía te ayudará a configurar y usar el servidor MCP de FRED Economic Data en diferentes entornos.

## 📋 Prerequisitos

1. **API Key de FRED**: Obtén tu API key gratuita en [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
2. **Python 3.9+** instalado en tu sistema
3. **uv** (Python package manager): Instalar con `pip install uv`

## 🔧 Instalación del Servidor

### Paso 1: Clonar el Repositorio

```bash
git clone <repository-url>
cd trabajoIA
```

### Paso 2: Instalar Dependencias

```bash
cd server
uv pip install -e .
```

### Paso 3: Configurar API Key

Crea un archivo `.env` en la carpeta `server/`:

```bash
FRED_API_KEY=tu_api_key_aqui
```

O configura la variable de entorno:

```bash
# Windows PowerShell
$env:FRED_API_KEY="tu_api_key_aqui"

# Windows CMD
set FRED_API_KEY=tu_api_key_aqui

# Linux/Mac
export FRED_API_KEY="tu_api_key_aqui"
```

---

## 🔌 Integración en Claude Desktop

### Configuración

1. **Localiza el archivo de configuración** según tu sistema operativo:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Edita el archivo de configuración** y agrega:

```json
{
  "mcpServers": {
    "fred-economic-data": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\agust\\OneDrive\\Documentos\\VSCODE\\trabajoIA\\server",
        "run",
        "fred-economic-data"
      ],
      "env": {
        "FRED_API_KEY": "tu_api_key_aqui"
      }
    }
  }
}
```

**⚠️ Importante**: Reemplaza la ruta con la ruta absoluta a tu carpeta `server`.

3. **Reinicia Claude Desktop** completamente (cierra y abre la aplicación).

### Verificación

1. Abre Claude Desktop
2. Busca el ícono de 🔌 o "MCP" en la interfaz
3. Deberías ver "fred-economic-data" listado como servidor conectado
4. Prueba con: *"Busca series sobre desempleo en Estados Unidos"*

---

## 💻 Integración en VSCode (Claude Dev / Cline)

### Con Claude Dev Extension

1. **Instala la extensión** [Claude Dev](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev) desde VSCode Marketplace

2. **Abre la configuración de MCP**:
   - Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac)
   - Busca: "Claude Dev: Open MCP Settings"

3. **Agrega el servidor**:

```json
{
  "mcpServers": {
    "fred-economic-data": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\agust\\OneDrive\\Documentos\\VSCODE\\trabajoIA\\server",
        "run",
        "fred-economic-data"
      ],
      "env": {
        "FRED_API_KEY": "tu_api_key_aqui"
      }
    }
  }
}
```

4. **Recarga VSCode**: `Ctrl+Shift+P` → "Developer: Reload Window"

### Con Cline Extension

1. **Instala [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.cline)** desde VSCode Marketplace

2. **Configura MCP Settings**:
   - Abre Cline en el sidebar
   - Haz clic en el ícono de configuración (⚙️)
   - Ve a la sección "MCP Servers"
   - Agrega la configuración JSON mostrada arriba

3. **Reinicia Cline** desde el panel de Cline

---

## 🤖 Integración en Claude Code (CLI)

### Configuración

1. **Localiza el archivo de configuración**:
   - **Windows**: `%USERPROFILE%\.claude\claude_config.json`
   - **macOS/Linux**: `~/.claude/claude_config.json`

2. **Crea o edita el archivo** y agrega:

```json
{
  "mcpServers": {
    "fred-economic-data": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\agust\\OneDrive\\Documentos\\VSCODE\\trabajoIA\\server",
        "run",
        "fred-economic-data"
      ],
      "env": {
        "FRED_API_KEY": "tu_api_key_aqui"
      }
    }
  }
}
```

3. **Inicia Claude Code**:

```bash
claude
```

### Verificación en Claude Code

Dentro de la sesión de Claude Code, ejecuta:

```
/mcp list
```

Deberías ver "fred-economic-data" listado. Luego prueba:

```
Busca la serie de tasa de desempleo de Estados Unidos
```

---

## 🧪 Pruebas de Funcionamiento

### Comandos de Prueba Básicos

1. **Búsqueda de Series**:
```
Busca series económicas sobre inflación en Estados Unidos
```

2. **Obtener Datos**:
```
Dame los datos de la serie UNRATE (tasa de desempleo) de los últimos 5 años
```

3. **Análisis Comparativo de GDP**:
```
Compara el GDP per capita de los países del G7 desde el año 2000
```

4. **Explorar Categorías**:
```
Muéstrame las categorías disponibles en FRED relacionadas con comercio internacional
```

### Herramientas Disponibles

El servidor MCP proporciona las siguientes herramientas:

- `search_fred_series` - Buscar series económicas
- `get_fred_series_observations` - Obtener datos de series
- `get_fred_tags` - Explorar tags disponibles
- `search_fred_related_tags` - Buscar tags relacionados
- `get_fred_series_by_tags` - Buscar series por tags
- `search_fred_series_tags` - Tags de búsqueda de series
- `search_fred_series_related_tags` - Tags relacionados de series
- `get_fred_series_tags` - Tags de una serie específica
- `get_fred_category` - Información de categorías
- `get_fred_category_children` - Subcategorías
- `get_fred_category_series` - Series en una categoría
- `analyze_gdp_cross_country` - **Análisis avanzado de GDP entre países**

---

## 🐛 Solución de Problemas

### El servidor no aparece conectado

1. **Verifica la API Key**: Asegúrate de que `FRED_API_KEY` esté correctamente configurada
2. **Verifica la ruta**: La ruta al directorio `server` debe ser absoluta y correcta
3. **Revisa los logs**:
   - Claude Desktop: Menú → View → Developer → Developer Tools → Console
   - VSCode: Output panel → Select "Claude Dev" or "Cline"
   - Claude Code: Busca mensajes de error en la terminal

### Error "command not found: uv"

Instala `uv`:
```bash
pip install uv
```

### Error de permisos

En Windows, ejecuta tu terminal/VSCode como administrador.

### El servidor se conecta pero no responde

1. Prueba el servidor manualmente:
```bash
cd server
uv run fred-economic-data
```

2. Verifica que todas las dependencias estén instaladas:
```bash
cd server
uv pip install -e .
```

---

## 📚 Recursos Adicionales

- [Documentación de FRED API](https://fred.stlouisfed.org/docs/api/fred/)
- [Guía de MCP Protocol](https://modelcontextprotocol.io/)
- [Arquitectura del Servidor](server/docs/architecture.md)
- [README Principal](README.md)

---

## 💡 Ejemplos de Uso Avanzado

### Análisis Económico Completo

```
Analiza la convergencia económica entre países de América Latina (México, Brasil,
Argentina, Chile, Colombia) usando GDP per capita constante desde 1990.
Incluye detección de quiebres estructurales y rankings.
```

### Comparación con Benchmark

```
Compara el crecimiento del GDP de países emergentes (China, India, Brasil)
contra Estados Unidos como benchmark, desde el año 2000, usando valores indexados.
```

### Análisis por Periodos

```
Analiza el GDP per capita PPP del G7 dividido por décadas desde 1980,
con análisis de crecimiento y convergencia.
```

---

## 🎯 Siguientes Pasos

1. ✅ Configura tu integración preferida
2. 🔍 Explora las series disponibles en FRED
3. 📊 Realiza tu primer análisis económico
4. 🚀 Experimenta con análisis comparativos avanzados
5. 📖 Lee la [documentación completa](README.md) para más detalles

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o consulta la documentación.
