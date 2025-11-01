# Version Update Guide

**Purpose:** Step-by-step process for updating the project version
**Audience:** Developers, Release Managers, Claude AI
**Estimated Time:** 15-20 minutes per release

---

## Table of Contents

1. [Pre-Release Checklist](#pre-release-checklist)
2. [Version Update Process](#version-update-process)
3. [Files to Read (Analysis Phase)](#files-to-read-analysis-phase)
4. [Files to Modify (Update Phase)](#files-to-modify-update-phase)
5. [Verification Steps](#verification-steps)
6. [Version Numbering Guidelines](#version-numbering-guidelines)
7. [Quick Reference Checklist](#quick-reference-checklist)

---

## Pre-Release Checklist

Before starting the version update process, ensure:

- [ ] All new features/fixes are implemented and tested
- [ ] All tests pass successfully
- [ ] Documentation is complete (API references, guides)
- [ ] You have identified all changes since last version
- [ ] You know the new version number (e.g., 0.1.4)
- [ ] You have a summary of what changed

---

## Version Update Process

The process consists of 5 phases:

```
PHASE 1: Analysis     → Read current state
PHASE 2: Planning     → Identify changes
PHASE 3: Version Bump → Update version numbers
PHASE 4: Changelog    → Document changes
PHASE 5: Release Notes → Create detailed notes
```

### PHASE 1: Analysis - Read Current State

Read these files to understand the current state:

#### 1.1 Read Current Version Files

Read these 3 files to see current version:

```python
# Files to read:
1. server/src/trabajo_ia_server/config.py          # Line ~24: SERVER_VERSION
2. server/src/trabajo_ia_server/__init__.py        # Line ~6: __version__
3. server/pyproject.toml                           # Line ~3: version
```

**Purpose:** Verify current version number (should be same in all 3 files)

**Example:** All three should show `"0.1.3"` if that's the current version

#### 1.2 Read CHANGELOG.md

```python
# File to read:
server/docs/Changelog/CHANGELOG.md
```

**Purpose:** Understand the format and see what was in previous releases

**Key Elements to Note:**
- Section format: `## [VERSION] - YYYY-MM-DD`
- Change categories: Added, Changed, Fixed, Removed, etc.
- Level of detail in descriptions
- Comparison links at bottom

#### 1.3 Read Latest Release Notes

```python
# File to read:
server/docs/Release_notes/RELEASE_NOTES_v{CURRENT_VERSION}.md
```

**Example:** If current is 0.1.3, read `RELEASE_NOTES_v0.1.3.md`

**Purpose:** Understand format and structure for release notes

**Key Elements to Note:**
- Front matter (Release Date, Type, Focus)
- Sections: Overview, What's New, Features, Examples, etc.
- Level of technical detail
- Code examples and use cases

### PHASE 2: Planning - Identify Changes

Before modifying files, document what changed:

#### 2.1 List New Features/Tools

Identify what was added since last version:

```python
# Questions to answer:
- What new tools were added?
- What new files were created?
- What new capabilities exist?
```

**Example for v0.1.4:**
- New tool: `get_fred_series_by_tags`
- New file: `series_by_tags.py`
- New capability: Tag-based series filtering with AND/NOT logic

#### 2.2 List Changes

Identify what was modified:

```python
# Questions to answer:
- Were existing tools modified?
- Were performance improvements made?
- Were bugs fixed?
- Were breaking changes introduced?
```

#### 2.3 Determine Version Number

Use semantic versioning: `MAJOR.MINOR.PATCH`

For our project (currently pre-1.0):
- `0.MINOR.PATCH`

Rules:
- **PATCH** (0.1.X): Bug fixes, documentation updates, minor tweaks
- **MINOR** (0.X.0): New features, tools, significant additions (backward compatible)
- **MAJOR** (X.0.0): Breaking changes, major rewrites (will be 1.0.0+ when stable)

**Current pattern:** Each new tool = minor version bump (0.1.3 → 0.1.4)

### PHASE 3: Version Bump - Update Version Numbers

Update version in exactly 3 files in this order:

#### 3.1 Update config.py

```python
# File: server/src/trabajo_ia_server/config.py
# Line: ~24

# OLD:
SERVER_VERSION: str = "0.1.3"

# NEW:
SERVER_VERSION: str = "0.1.4"
```

**Use Edit tool:**
```python
Edit(
    file_path="server/src/trabajo_ia_server/config.py",
    old_string='    SERVER_VERSION: str = "0.1.3"',
    new_string='    SERVER_VERSION: str = "0.1.4"'
)
```

#### 3.2 Update __init__.py

```python
# File: server/src/trabajo_ia_server/__init__.py
# Line: ~6

# OLD:
__version__ = "0.1.3"

# NEW:
__version__ = "0.1.4"
```

**Use Edit tool:**
```python
Edit(
    file_path="server/src/trabajo_ia_server/__init__.py",
    old_string='__version__ = "0.1.3"',
    new_string='__version__ = "0.1.4"'
)
```

#### 3.3 Update pyproject.toml

```python
# File: server/pyproject.toml
# Line: ~3

# OLD:
version = "0.1.3"

# NEW:
version = "0.1.4"
```

**Use Edit tool:**
```python
Edit(
    file_path="server/pyproject.toml",
    old_string='version = "0.1.3"',
    new_string='version = "0.1.4"'
)
```

### PHASE 4: Changelog - Update CHANGELOG.md

Add a new section at the top of CHANGELOG.md (after the header, before previous versions).

#### 4.1 Read Current CHANGELOG.md

```python
# Already done in Phase 1, but review the format again
```

#### 4.2 Add New Version Section

Insert new section at line ~8 (after the project description, before [0.1.3]):

```markdown
## [0.1.4] - 2025-11-01

### Added - [Brief Description]

[Detailed description of what was added]

**Key Features:**
- Feature 1
- Feature 2
- Feature 3

**Use Cases:**
1. Use case 1
2. Use case 2

**Examples:**
```python
# Example code
```

**Performance:**
- Metric 1
- Metric 2

**Files Added:**
- file1.py
- file2.md

**Files Modified:**
- file3.py
- file4.py
```

**Use Edit tool** to insert after line 7 (after the semver description).

#### 4.3 Format Guidelines

Follow these rules:
- **Date Format:** `YYYY-MM-DD`
- **Categories:** Added, Changed, Fixed, Removed, Deprecated, Security
- **Level of Detail:** Enough to understand changes without reading code
- **Code Examples:** Include where helpful
- **Bullet Points:** Use `-` for main points, indented for sub-points

### PHASE 5: Release Notes - Create RELEASE_NOTES_vX.X.X.md

Create a new comprehensive release notes document.

#### 5.1 Create New Release Notes File

```python
# File: server/docs/Release_notes/RELEASE_NOTES_v0.1.4.md
```

#### 5.2 Structure

Use this template structure (500-700 lines typical):

```markdown
# Release Notes - Trabajo IA MCP Server v{VERSION}

**Release Date:** {DATE}
**Type:** {Feature Addition|Bug Fix|Performance|Breaking Change}
**Focus:** {One-line summary}

---

## Overview

[2-3 paragraph overview of the release]

### Key Achievement

[Bold statement about main accomplishment]

---

## What's New

### New Tool: `{tool_name}`

[Description and basic usage]

**Core Functionality:**
```python
# Basic examples
```

**Response Format:**
```json
{
  // Example response
}
```

---

## Features

### 1. [Feature Name]

[Detailed description]

```python
# Examples
```

### 2. [Feature Name]

[Continue for all features...]

---

## Use Cases

### 1. [Use Case Title]

**Scenario:** [Description]

**Solution:**
```python
# Code example
```

**Benefits:**
- Benefit 1
- Benefit 2

[Continue for 5-7 use cases...]

---

## Parameters

### Required Parameters

[Document required params with examples]

### Optional Parameters

[Document optional params with examples]

---

## Performance

- **Response Time:** [metrics]
- **Default Limit:** [value]
- **JSON Format:** [description]
- **Retry Mechanism:** [description]

---

## Examples

### Example 1: [Title]

```python
# Code
```

**Output:**
```
# Result
```

**Use Case:** [When to use this]

[Continue for 5-7 examples...]

---

## Breaking Changes

[List any breaking changes, or state "None"]

---

## Compatibility

### Backwards Compatibility

[Describe compatibility with previous versions]

### Dependencies

[List any new dependencies or changes]

---

## Installation & Upgrade

### New Installation

```bash
cd server
uv sync
```

### Upgrade from v{PREVIOUS}

```bash
cd server
uv sync
```

### Verify Installation

```python
# Verification code
```

---

## Known Issues

[List any known issues, or state "None currently identified"]

---

## Future Enhancements

Planned for v{NEXT}:
- Feature 1
- Feature 2

---

## Files Added

- List of new files with descriptions

## Files Modified

- List of modified files with changes

---

## Summary

**v{VERSION} {brief description}:**

- Point 1
- Point 2
- Point 3

**Upgrade recommended for:**
- Audience 1
- Audience 2

---

**Version:** {VERSION}
**Release Date:** {DATE}
**Status:** Production Ready
**Recommended:** Yes
```

---

## Files to Read (Analysis Phase)

Complete list in order:

| # | File | Purpose | Key Info to Extract |
|---|------|---------|---------------------|
| 1 | `src/trabajo_ia_server/config.py` | Current version | Line ~24: `SERVER_VERSION` |
| 2 | `src/trabajo_ia_server/__init__.py` | Current version | Line ~6: `__version__` |
| 3 | `pyproject.toml` | Current version | Line ~3: `version` |
| 4 | `docs/Changelog/CHANGELOG.md` | Changelog format | Section structure, categories |
| 5 | `docs/Release_notes/RELEASE_NOTES_v{current}.md` | Release notes format | Structure, sections, detail level |

---

## Files to Modify (Update Phase)

Complete list in order:

| # | File | Action | Location | What to Change |
|---|------|--------|----------|----------------|
| 1 | `src/trabajo_ia_server/config.py` | Edit | Line ~24 | `SERVER_VERSION` value |
| 2 | `src/trabajo_ia_server/__init__.py` | Edit | Line ~6 | `__version__` value |
| 3 | `pyproject.toml` | Edit | Line ~3 | `version` value |
| 4 | `docs/Changelog/CHANGELOG.md` | Edit | After line 7 | Insert new version section |
| 5 | `docs/Release_notes/RELEASE_NOTES_v{new}.md` | Create | New file | Full release notes |

---

## Verification Steps

After completing all updates, verify:

### 1. Version Consistency Check

```bash
# Run these commands to verify all versions match:
cd server

# Check config.py
grep "SERVER_VERSION" src/trabajo_ia_server/config.py

# Check __init__.py
grep "__version__" src/trabajo_ia_server/__init__.py

# Check pyproject.toml
grep "^version" pyproject.toml
```

**Expected:** All three should show the same new version (e.g., "0.1.4")

### 2. Test Import

```python
# Test that version is accessible
from trabajo_ia_server import __version__
print(__version__)  # Should print new version
```

### 3. Run Tests

```bash
cd server
uv run pytest
```

**Expected:** All tests pass

### 4. Test New Feature

```python
# Test the new feature/tool added in this version
# Example for v0.1.4:
from trabajo_ia_server.tools.fred.series_by_tags import get_series_by_tags
result = get_series_by_tags("usa;monthly", limit=5)
print(result)  # Should work without errors
```

### 5. Documentation Check

- [ ] CHANGELOG.md has new version section
- [ ] Release notes file exists and is complete
- [ ] All code examples in docs are accurate
- [ ] API references are updated (if applicable)

### 6. Git Status Check

```bash
# Check what files were modified
git status

# Review changes
git diff
```

**Expected changes:**
- Modified: config.py, __init__.py, pyproject.toml, CHANGELOG.md
- Added: RELEASE_NOTES_v{new}.md
- Plus any new feature files

---

## Version Numbering Guidelines

### Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

Current phase: Pre-1.0 (`0.MINOR.PATCH`)

### When to Bump Each Number

#### PATCH (0.1.X → 0.1.Y)

Use for:
- Bug fixes
- Documentation updates
- Minor code improvements
- Performance optimizations (minor)
- Typo corrections

**Example:** 0.1.3 → 0.1.4 if only fixing a bug

#### MINOR (0.X.0 → 0.Y.0)

Use for:
- New tools/features
- New API endpoints
- Significant enhancements
- New capabilities
- Backward-compatible changes

**Example:** 0.1.4 → 0.2.0 if adding multiple new tools

**Current Practice:** One new tool = minor bump

#### MAJOR (X.0.0 → Y.0.0)

Use for:
- Breaking changes
- Complete rewrites
- API changes that break compatibility
- Removal of features
- Stable release (1.0.0)

**Example:** 0.9.0 → 1.0.0 when ready for production

### Current Pattern (v0.1.x series)

We're currently in the 0.1.x series where:
- Each new FRED tool = minor version bump
- 0.1.0: Initial release with `fetch_fred_series`
- 0.1.1: Added `search_fred_series`
- 0.1.2: Performance optimization
- 0.1.3: Added `get_fred_tags`
- 0.1.4: Added `get_fred_series_by_tags` (current)

**Next:** When we have 5-6 core tools complete, consider 0.2.0 or plan for 1.0.0

---

## Quick Reference Checklist

Use this for quick updates:

```
□ PHASE 1: READ FILES
  □ Read config.py (current version)
  □ Read __init__.py (current version)
  □ Read pyproject.toml (current version)
  □ Read CHANGELOG.md (format reference)
  □ Read latest RELEASE_NOTES_v*.md (format reference)

□ PHASE 2: PLAN
  □ Identify all changes since last version
  □ List new features/tools
  □ List modifications/fixes
  □ Determine new version number
  □ Write summary of changes

□ PHASE 3: VERSION BUMP
  □ Update config.py (SERVER_VERSION)
  □ Update __init__.py (__version__)
  □ Update pyproject.toml (version)

□ PHASE 4: CHANGELOG
  □ Add new version section to CHANGELOG.md
  □ Include: Added/Changed/Fixed sections
  □ Include: Examples and use cases
  □ Include: Files added/modified

□ PHASE 5: RELEASE NOTES
  □ Create new RELEASE_NOTES_v{version}.md
  □ Write Overview section
  □ Document What's New section
  □ List all Features (detailed)
  □ Provide 5-7 Use Cases
  □ Document all Parameters
  □ Provide 5-7 Examples
  □ Document Performance metrics
  □ List Breaking Changes (if any)
  □ Document Compatibility
  □ List Files Added/Modified

□ VERIFICATION
  □ All 3 version files show same version
  □ CHANGELOG has new section
  □ Release notes file created
  □ Run: grep version check commands
  □ Run: pytest
  □ Test new feature manually
  □ Review git status/diff

□ POST-RELEASE (if applicable)
  □ Git commit with message "chore: Release v{version}"
  □ Git tag v{version}
  □ Git push with tags
  □ Update any external documentation
```

---

## Common Mistakes to Avoid

### 1. Inconsistent Version Numbers

❌ **Wrong:** Different versions in different files
```
config.py:      "0.1.4"
__init__.py:    "0.1.3"    # Forgot to update
pyproject.toml: "0.1.4"
```

✅ **Right:** Same version everywhere
```
config.py:      "0.1.4"
__init__.py:    "0.1.4"
pyproject.toml: "0.1.4"
```

### 2. Wrong CHANGELOG Format

❌ **Wrong:** Inconsistent date format
```markdown
## [0.1.4] - November 1, 2025  # Wrong format
```

✅ **Right:** ISO date format
```markdown
## [0.1.4] - 2025-11-01
```

### 3. Incomplete Release Notes

❌ **Wrong:** Minimal information
```markdown
# Release Notes v0.1.4

Added new tool.
```

✅ **Right:** Comprehensive documentation
```markdown
# Release Notes v0.1.4

## Overview
[Detailed overview...]

## Features
[Detailed features...]

## Examples
[Multiple examples...]
```

### 4. Missing Verification

❌ **Wrong:** Skip testing after version bump

✅ **Right:** Always test:
```bash
# Test version import
# Run pytest
# Test new feature manually
```

### 5. Wrong Version Number Choice

❌ **Wrong:** Using PATCH for new feature
```
0.1.3 → 0.1.3.1  # Wrong for new tool
```

✅ **Right:** Using MINOR for new feature
```
0.1.3 → 0.1.4    # Correct for new tool
```

---

## Examples

### Example 1: New Tool Release (0.1.3 → 0.1.4)

**Scenario:** Added `get_fred_series_by_tags` tool

**Changes:**
- New file: `series_by_tags.py`
- Modified: `server.py` (registration)
- Modified: `__init__.py` (export)
- New doc: `FRED_SERIESBYTAGS_REFERENCE.MD`

**Version Decision:** Minor bump (new feature)

**Process:**
1. Read current version: 0.1.3
2. Determine new version: 0.1.4
3. Update 3 version files: 0.1.3 → 0.1.4
4. Add CHANGELOG section for 0.1.4
5. Create RELEASE_NOTES_v0.1.4.md
6. Verify and test

### Example 2: Bug Fix Release (hypothetical 0.1.4 → 0.1.5)

**Scenario:** Fixed error handling in search_fred_series

**Changes:**
- Modified: `search_series.py` (better error messages)
- Modified: tests (added error cases)

**Version Decision:** Patch bump (bug fix)

**Process:**
1. Read current version: 0.1.4
2. Determine new version: 0.1.5
3. Update 3 version files: 0.1.4 → 0.1.5
4. Add CHANGELOG section for 0.1.5 under "### Fixed"
5. Create brief RELEASE_NOTES_v0.1.5.md
6. Verify and test

### Example 3: Major Feature Set (hypothetical 0.1.x → 0.2.0)

**Scenario:** Added 3 new tools and refactored architecture

**Changes:**
- Multiple new tools
- Architecture changes
- Performance improvements
- Breaking changes in configuration

**Version Decision:** Minor bump (in pre-1.0) or Major (if breaking)

**Process:**
1. Read current version: 0.1.6
2. Determine new version: 0.2.0 (significant changes)
3. Update 3 version files: 0.1.6 → 0.2.0
4. Add detailed CHANGELOG section with "### Added", "### Changed", "### Breaking Changes"
5. Create comprehensive RELEASE_NOTES_v0.2.0.md
6. Document migration path for breaking changes
7. Extensive verification and testing

---

## Automation Considerations

For AI agents or scripts, this process can be semi-automated:

### Automated Steps
- ✅ Version number replacement (Edit tool)
- ✅ File reading (Read tool)
- ✅ CHANGELOG section generation (template-based)
- ✅ Release notes structure (template-based)

### Manual/Review Steps
- ⚠️ Determining version number (requires judgment)
- ⚠️ Writing detailed descriptions (requires context)
- ⚠️ Creating examples (requires testing)
- ⚠️ Final review (requires human judgment)

### Recommended Workflow for AI

1. AI reads current state (Phase 1)
2. Human provides: new version number + change summary
3. AI executes version bumps (Phase 3)
4. AI generates CHANGELOG and Release Notes (Phases 4-5)
5. Human reviews and approves
6. AI runs verification tests
7. Human does final checks and git operations

---

## File Paths Reference

For easy copying:

```
# Version files (to modify):
server/src/trabajo_ia_server/config.py
server/src/trabajo_ia_server/__init__.py
server/pyproject.toml

# Documentation files (to modify/create):
server/docs/Changelog/CHANGELOG.md
server/docs/Release_notes/RELEASE_NOTES_v{VERSION}.md

# Reference files (to read):
server/docs/Release_notes/RELEASE_NOTES_v0.1.3.md
server/docs/guides/IMPLEMENTACION_NUEVA_TOOL_GUIA.md
```

---

## Troubleshooting

### Issue: Version mismatch detected

**Symptom:**
```python
import trabajo_ia_server
print(trabajo_ia_server.__version__)  # Shows 0.1.3
# But config.SERVER_VERSION shows 0.1.4
```

**Solution:**
1. Check all 3 files have same version
2. Restart Python interpreter / reload module
3. Run `uv sync` to reinstall package

### Issue: CHANGELOG merge conflict

**Symptom:** Git shows conflicts in CHANGELOG.md

**Solution:**
1. Always add new version at top
2. Keep both changes if simultaneous releases
3. Reorder chronologically (newest first)

### Issue: Tests fail after version bump

**Symptom:** Tests that check version numbers fail

**Solution:**
1. Update test files that hardcode version checks
2. Use dynamic version import in tests:
   ```python
   from trabajo_ia_server import __version__
   assert __version__.startswith("0.1")
   ```

---

## Summary

**Quick Process Summary:**

1. **Read** current state (5 files)
2. **Plan** changes and version number
3. **Update** version in 3 files
4. **Document** in CHANGELOG.md
5. **Create** comprehensive release notes
6. **Verify** all changes

**Time Estimate:** 15-20 minutes per release

**Critical Success Factors:**
- ✅ Version consistency across all files
- ✅ Complete documentation
- ✅ Thorough testing
- ✅ Clear communication of changes

---

**Guide Version:** 1.0.0
**Last Updated:** 2025-11-01
**Applies to:** Trabajo IA MCP Server v0.1.3+
