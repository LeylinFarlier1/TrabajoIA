# Trabajo IA MCP Server - Documentation Index

Welcome to the Trabajo IA MCP Server documentation. This index will help you navigate through all available documentation.

## 📚 Quick Start

New to the project? Start here:

1. **[Quick Start Guide](../../QUICKSTART.md)** - Installation and setup for Claude Desktop, VSCode, and Claude Code
2. **[Main README](../README.md)** - Project overview, installation, and basic usage
3. **[Architecture Guide](architecture.md)** - System design and architecture
4. **[Version Update Guide](guides/VERSION_UPDATE_GUIDE.md)** - Step-by-step release checklist

## 📖 Core Documentation

### Project Documentation (Root Level)

- **[README.md](../README.md)** - Main project documentation
  - Features overview
  - Installation instructions
  - Available tools and usage examples
  - Quick start guide

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
  - Release notes for all versions
  - Feature additions and bug fixes
  - Breaking changes and migrations
  - Upgrade guides

- **[RELEASE_NOTES_v0.1.9.md](Release_notes/RELEASE_NOTES_v0.1.9.md)** - Latest release details
  - What's new in v0.1.9: cache, rate limiting, telemetry, and internal health diagnostics
  - Usage examples
  - Performance metrics
  - Migration instructions

## 🏗️ Architecture & Design

### [architecture.md](architecture.md)
Comprehensive architecture documentation covering:
- System overview and principles
- Directory structure explanation
- Module responsibilities
- Data flow diagrams
- Design patterns used
- Extension points
- Testing strategy
- Security considerations
- Performance optimizations

**Topics covered:**
- Separation of concerns
- Dependency injection
- Type safety
- Error handling strategy
- Configuration management
- Logging architecture
- Future enhancements

## 📘 Guides

Located in `docs/guides/`:

### [VERSION_UPDATE_GUIDE.md](guides/VERSION_UPDATE_GUIDE.md)
Step-by-step release instructions:
- Version consistency checklist
- Required documentation updates
- Testing and verification workflow
- Semantic versioning guidance

**Use this when:**
- Preparing a new release
- Auditing documentation coverage
- Coordinating handoff between contributors

### [MCP_PROJECT_TESTING_GUIDE.md](guides/MCP_PROJECT_TESTING_GUIDE.md)
Comprehensive testing and prompting playbook:
- Architecture refresher and tool catalog
- Prompt templates for unit and workflow tests
- Troubleshooting guidance for common issues
- Recommended validation workflows

**Use this to:**
- Design structured QA prompts
- Understand MCP request flows
- Align on testing expectations across teams

### [IMPLEMENTACION_NUEVA_TOOL_GUIA.md](guides/IMPLEMENTACION_NUEVA_TOOL_GUIA.md)
How-to guide for adding a new MCP tool:
- Environment setup checklist
- Template for tool scaffolding
- Validation and logging patterns
- Publishing and documentation steps

**Use this to:**
- Prototype new FRED integrations
- Ensure new tools follow project conventions
- Share onboarding material with new contributors

## 🔧 API Reference

### Tools Documentation (12 MCP Tools)

#### FRED Data Tools (11 tools)

**1. search_fred_series**
- **Location**: `src/trabajo_ia_server/tools/fred/search_series.py`
- Advanced search with filters, categories, tags, pagination
- **See**: [README - search_fred_series](../README.md#1-search_fred_series-new-in-v011)

**2. get_fred_series_observations**
- **Location**: `src/trabajo_ia_server/tools/fred/observations.py`
- Fetch historical time-series data with date ranges
- **See**: [README - get_fred_series_observations](../README.md#2-fetch_fred_series)

**3-8. Tag Management Tools**
- `get_fred_tags` - Discover available tags
- `search_fred_related_tags` - Find related tags
- `get_fred_series_by_tags` - Filter series by tags
- `search_fred_series_tags` - Tags for series searches
- `search_fred_series_related_tags` - Related tags in searches
- `get_fred_series_tags` - Tags for specific series

**9-11. Category Tools**
- `get_fred_category` - Category information
- `get_fred_category_children` - Sub-categories
- `get_fred_category_series` - Series in a category

#### Advanced Workflows (1 tool)

**analyze_gdp_cross_country**
- **Location**: `src/trabajo_ia_server/workflows/analyze_gdp.py`
- Multi-country GDP analysis with:
  - 238 countries + presets (G7, G20, BRICS, LATAM, etc.)
  - Structural breaks detection
  - Convergence analysis (sigma/beta)
  - Growth metrics (CAGR, volatility, stability)
  - Rankings and comparisons
- **See**: [GDP Workflow Reference](workflows/ANALYZE_GDP_CROSS_COUNTRY_REFERENCE.md)

#### System Tools (1 tool)

**system_health**
- **Location**: `src/trabajo_ia_server/tools/system/health.py`
- Cache status, rate limiter state, metrics snapshot
- **See**: [README - system_health](../README.md#3-system_health)

## 💡 Usage Examples

### Basic FRED Queries

**Search for series:**
```
Busca series sobre desempleo en Estados Unidos
```

**Get historical data:**
```
Dame los datos mensuales de la serie UNRATE desde 2020
```

**Explore categories:**
```
¿Qué categorías hay disponibles sobre comercio internacional?
```

### Advanced GDP Analysis Examples

**G7 Comparative Analysis:**
```
Analiza el GDP per capita constante del G7 desde 1980 hasta 2010,
incluyendo detección de quiebres estructurales y análisis de convergencia
```

**Latin America Economic Study:**
```
Compara la convergencia económica de países LATAM (México, Brasil, Argentina,
Chile, Colombia) usando GDP per capita PPP desde 1990, con análisis por décadas
```

**Emerging Markets Growth:**
```
Analiza el crecimiento del GDP de BRICS (Brasil, Rusia, India, China, Sudáfrica)
en comparación con Estados Unidos como benchmark, con valores indexados
```

**Structural Breaks Detection:**
```
Detecta quiebres estructurales en el crecimiento económico de países del G20
desde 1980, mostrando períodos de crisis y estabilización
```

**Custom Country Analysis:**
```
Analiza GDP per capita constante de España, Italia y Grecia desde 1995,
detectando el impacto de la crisis europea 2008-2012
```

### System Monitoring

**Check server health:**
```
Muéstrame el estado del servidor MCP y sus métricas de cache
```

## 🧪 Testing

### Test Documentation

- **Unit Tests**: `tests/unit/` - Component-level tests
- **Integration Tests**: `tests/integration/` - End-to-end tests
- **Fixtures**: `tests/fixtures/` - Test data and mocks

**Running tests:**
```bash
# All tests
pytest

# With coverage
pytest --cov=trabajo_ia_server

# Specific module
pytest tests/unit/tools/test_fred_search.py
```

## 🗂️ Documentation Structure

```
server/
├── README.md                          # Main documentation
├── CHANGELOG.md                       # Version history
├── Release_notes/RELEASE_NOTES_v0.1.9.md # Latest release
│
└── docs/                              # Documentation folder
    ├── README.md                      # This file
    ├── architecture.md                # Architecture guide
    │
    ├── api/                           # API reference (future)
    │   └── (To be added)
    │
    └── guides/                        # How-to guides
        ├── VERSION_UPDATE_GUIDE.md           # Release checklist
        ├── MCP_PROJECT_TESTING_GUIDE.md      # Prompting & QA playbook
        └── IMPLEMENTACION_NUEVA_TOOL_GUIA.md # New tool workflow
```

## 🎯 Documentation by Use Case

### I want to...

#### Learn about the project
→ Start with [README.md](../README.md)

#### Understand the architecture
→ Read [architecture.md](architecture.md)

#### Prepare a release
→ Review [VERSION_UPDATE_GUIDE.md](guides/VERSION_UPDATE_GUIDE.md)

#### See what's new in v0.1.9
→ Check [RELEASE_NOTES_v0.1.9.md](Release_notes/RELEASE_NOTES_v0.1.9.md)

#### Use the search tool
→ See examples in [README - search_fred_series](../README.md#1-search_fred_series-new-in-v011)

#### Add a new tool
→ Follow [architecture.md - Extension Points](architecture.md#extension-points)

#### Review all changes
→ Read [CHANGELOG.md](../CHANGELOG.md)

#### Understand project structure
→ See [architecture.md](architecture.md#project-structure)

## 🔌 Integration Guide

### Quick Setup by Platform

For detailed step-by-step instructions, see **[QUICKSTART.md](../../QUICKSTART.md)**

#### Claude Desktop
1. Edit: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
2. Add MCP server configuration
3. Restart Claude Desktop
4. Look for 🔌 icon to verify connection

#### VSCode (Claude Dev / Cline)
1. Install Claude Dev or Cline extension
2. Open MCP Settings: `Ctrl+Shift+P` → "Claude Dev: Open MCP Settings"
3. Add server configuration
4. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

#### Claude Code (CLI)
1. Edit: `~/.claude/claude_config.json`
2. Add MCP server configuration
3. Start: `claude`
4. Verify: `/mcp list`

### Configuration Template

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
        "FRED_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**⚠️ Important**: Replace the path with your absolute path to the `server` directory.

## 🐛 Troubleshooting

### Server Not Connecting

**Claude Desktop:**
- Open Developer Tools: Menu → View → Developer → Developer Tools
- Check Console for error messages
- Verify API key is correct in config
- Ensure absolute path to server directory is correct

**VSCode:**
- Check Output panel: View → Output → Select "Claude Dev" or "Cline"
- Verify extension is installed and enabled
- Reload window after config changes
- Test server manually: `cd server && uv run fred-economic-data`

**Claude Code:**
- Check terminal output for startup errors
- Run `/mcp list` to see connected servers
- Verify config file location: `~/.claude/claude_config.json`
- Test server: `cd server && python -m trabajo_ia_server.server`

### API Key Issues

**Error: "Missing FRED_API_KEY"**
- Check `.env` file in server directory has `FRED_API_KEY=your_key`
- OR ensure API key is in MCP config under `env` section
- Get free key: https://fred.stlouisfed.org/docs/api/api_key.html

**Error: "Invalid API Key"**
- Verify key is active on FRED website
- Check for extra spaces or quotes in key
- Try regenerating key on FRED website

### Rate Limiting

**Error: "Rate limit exceeded"**
- Server implements automatic rate limiting (120 req/min)
- Wait 60 seconds and retry
- Check `system_health` tool for rate limiter status

### Installation Issues

**Error: "command not found: uv"**
```bash
pip install uv
```

**Error: "Module not found"**
```bash
cd server
uv pip install -e .
# or
pip install -e .
```

**Permission denied (Windows)**
- Run terminal/VSCode as Administrator
- Check antivirus isn't blocking Python execution

### Testing Your Setup

**1. Manual server test:**
```bash
cd server
python -m trabajo_ia_server.server
# Should start without errors
```

**2. Test with simple query:**
```
Busca la serie UNRATE
```

**3. Check system health:**
```
@workspace Muéstrame el system_health
```

## 🔄 Documentation Standards

All documentation in this project follows:

- **Markdown format** - GitHub-flavored markdown
- **Clear structure** - Headers, lists, code blocks
- **Examples** - Real-world usage examples
- **Links** - Cross-references between documents
- **Version info** - Clearly marked version-specific content

## 📝 Contributing to Documentation

When adding documentation:

1. **Location**:
   - Core docs → `docs/`
   - Guides → `docs/guides/`
   - API reference → `docs/api/`
   - Project info → root level

2. **Format**:
   - Use markdown (.md)
   - Include code examples
   - Add cross-references
   - Keep it concise

3. **Update this index** when adding new docs

## 🔗 External Resources

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Python Packaging Guide](https://packaging.python.org/)

## 📞 Getting Help

- Review documentation in this folder
- Check [CHANGELOG.md](../CHANGELOG.md) for known issues
- Read error messages and logs carefully
- Test with provided examples

---

**Last Updated**: 2025-11-10 (v0.1.9)
**Documentation Version**: 2.0
