# Trabajo IA MCP Server - Documentation Index

Welcome to the Trabajo IA MCP Server documentation. This index will help you navigate through all available documentation.

## 📚 Quick Start

New to the project? Start here:

1. **[Main README](../README.md)** - Project overview, installation, and basic usage
2. **[Architecture Guide](architecture.md)** - System design and architecture
3. **[Migration Guide](guides/MIGRATION_GUIDE.md)** - Upgrading from older versions

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

- **[RELEASE_NOTES_v0.1.1.md](../RELEASE_NOTES_v0.1.1.md)** - Latest release details
  - What's new in v0.1.1
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

### [MIGRATION_GUIDE.md](guides/MIGRATION_GUIDE.md)
Step-by-step migration instructions:
- From v0.1.0 to v0.1.1
- File mapping (old → new)
- Code changes required
- Import updates
- Configuration changes
- Troubleshooting common issues

**Use this when:**
- Upgrading to a new version
- Adapting custom code
- Understanding structural changes

### [REORGANIZATION_SUMMARY.md](guides/REORGANIZATION_SUMMARY.md)
Complete reorganization documentation:
- Before/after structure comparison
- All files created/modified
- Improvements implemented
- Verification steps
- Impact analysis

**Use this to:**
- Understand the project restructuring
- Review organizational decisions
- Track all changes made during reorganization

## 🔧 API Reference

### Tools Documentation

#### 1. search_fred_series
**Location**: `src/trabajo_ia_server/tools/fred/search_series.py`

Advanced FRED series search with:
- Full-text search
- Category filtering
- Tag-based filtering
- Pagination support
- Retry mechanism

**See**: [README - search_fred_series](../README.md#1-search_fred_series-new-in-v011)

#### 2. fetch_fred_series
**Location**: `src/trabajo_ia_server/tools/fred/fetch_series.py`

Fetch historical observations:
- Date range filtering
- Data validation
- Metadata inclusion

**See**: [README - fetch_fred_series](../README.md#2-fetch_fred_series)

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
├── RELEASE_NOTES_v0.1.1.md           # Latest release
│
└── docs/                              # Documentation folder
    ├── README.md                      # This file
    ├── architecture.md                # Architecture guide
    │
    ├── api/                           # API reference (future)
    │   └── (To be added)
    │
    └── guides/                        # How-to guides
        ├── MIGRATION_GUIDE.md         # Version migration
        └── REORGANIZATION_SUMMARY.md  # Project reorganization
```

## 🎯 Documentation by Use Case

### I want to...

#### Learn about the project
→ Start with [README.md](../README.md)

#### Understand the architecture
→ Read [architecture.md](architecture.md)

#### Upgrade from v0.1.0
→ Follow [MIGRATION_GUIDE.md](guides/MIGRATION_GUIDE.md)

#### See what's new in v0.1.1
→ Check [RELEASE_NOTES_v0.1.1.md](../RELEASE_NOTES_v0.1.1.md)

#### Use the search tool
→ See examples in [README - search_fred_series](../README.md#1-search_fred_series-new-in-v011)

#### Add a new tool
→ Follow [architecture.md - Extension Points](architecture.md#extension-points)

#### Review all changes
→ Read [CHANGELOG.md](../CHANGELOG.md)

#### Understand project structure
→ See [REORGANIZATION_SUMMARY.md](guides/REORGANIZATION_SUMMARY.md)

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

**Last Updated**: 2025-11-01 (v0.1.1)
