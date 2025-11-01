# FRED Category Tool – API Reference
## Tool: get_fred_category

**Endpoint:** `https://api.stlouisfed.org/fred/category`

**Description:** Get information about a specific FRED category. Essential for navigating FRED's hierarchical taxonomy of economic data.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Category Tree Navigation](#category-tree-navigation)
7. [Common Categories](#common-categories)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Best Practices](#best-practices)
11. [Related Tools](#related-tools)

---

## Overview

The `get_fred_category` tool retrieves metadata about a specific FRED category. FRED organizes its 800,000+ economic data series into a hierarchical taxonomy of categories, forming a tree structure that makes data discovery and organization intuitive.

### Key Features

- **Category Metadata**: Get ID, name, parent ID, and optional notes
- **Tree Navigation**: Use parent_id to navigate up the category hierarchy
- **Root Access**: Start from root (category_id=0) and explore downward
- **Fast Queries**: Typical response time < 0.5s
- **Compact JSON**: AI-optimized format
- **Error Handling**: Clear messages for invalid categories

### Why Use Categories?

Categories provide:
- **Organization**: Logical grouping of related economic data
- **Discovery**: Browse series by topic instead of searching
- **Context**: Understand what type of data a series represents
- **Relationships**: Find related series in same category
- **Hierarchy**: Navigate from broad topics to specific data

---

## Parameters

### Required Parameters

#### `category_id` (integer, REQUIRED)

The ID for a FRED category.

**Format:** Non-negative integer

**Examples:**
```python
0          # Root category
125        # Trade Balance
32991      # Money, Banking, & Finance
32992      # National Accounts
3008       # Population, Employment, & Labor Markets
32455      # Business Cycle Expansions & Contractions
```

**Important Notes:**
- Must be a valid FRED category ID
- Root category is always ID=0
- Cannot be negative
- Some category IDs may not exist (returns error)

**How to Find Category IDs:**
- Start from root (0) and navigate down
- Use FRED website to browse categories
- Category IDs are shown in FRED URLs
- Use related tools (category/children) to discover child categories

---

## Response Format

### Success Response

```json
{
  "tool": "get_category",
  "data": {
    "id": 125,
    "name": "Trade Balance",
    "parent_id": 13,
    "notes": "Optional description of category (if available)"
  },
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125
  }
}
```

### Fields Description

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| `id` | integer | Category ID | ✅ Yes |
| `name` | string | Category name | ✅ Yes |
| `parent_id` | integer | Parent category ID | ✅ Yes |
| `notes` | string | Category description/notes | ❌ Optional |

**Notes:**
- Root category (id=0) has `parent_id=0` (self-referencing)
- Top-level categories have `parent_id=0`
- `notes` field only present if category has description
- All IDs are integers

---

## Usage Examples

### Example 1: Get Root Category

**Goal:** Start exploring FRED category tree.

```python
result = get_fred_category(0)
```

**Response:**
```json
{
  "tool": "get_category",
  "data": {
    "id": 0,
    "name": "Categories",
    "parent_id": 0
  },
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 0
  }
}
```

**Insight:** Root category is named "Categories" and has parent_id=0 (self).

---

### Example 2: Get Trade Balance Category

**Goal:** Understand what Trade Balance category contains.

```python
result = get_fred_category(125)
```

**Response:**
```json
{
  "data": {
    "id": 125,
    "name": "Trade Balance",
    "parent_id": 13
  }
}
```

**Insight:** Trade Balance is a child of category 13 (likely "International Data").

---

### Example 3: Get Top-Level Category

**Goal:** Explore a major category group.

```python
result = get_fred_category(32991)
```

**Response:**
```json
{
  "data": {
    "id": 32991,
    "name": "Money, Banking, & Finance",
    "parent_id": 0
  }
}
```

**Insight:** Money, Banking, & Finance is a top-level category (parent=0).

---

### Example 4: Get National Accounts

**Goal:** Find economic accounting data.

```python
result = get_fred_category(32992)
```

**Response:**
```json
{
  "data": {
    "id": 32992,
    "name": "National Accounts",
    "parent_id": 0
  }
}
```

**Insight:** Another top-level category for GDP and national accounting data.

---

### Example 5: Navigate Up the Tree

**Goal:** Find parent category of Trade Balance.

```python
import json

# Get Trade Balance category
trade = get_fred_category(125)
data = json.loads(trade)
parent_id = data["data"]["parent_id"]

# Get parent category
parent = get_fred_category(parent_id)
parent_data = json.loads(parent)
print(f"Parent: {parent_data['data']['name']}")
```

**Result:** Navigate from specific category to broader category.

---

### Example 6: Check Category Existence

**Goal:** Validate category ID before using.

```python
result = get_fred_category(999999999)
data = json.loads(result)

if "error" in data:
    print(f"Category doesn't exist: {data['error']}")
else:
    print(f"Category found: {data['data']['name']}")
```

**Use Case:** Error handling for user-provided IDs.

---

### Example 7: Batch Category Lookup

**Goal:** Get info for multiple categories.

```python
category_ids = [32991, 32992, 3008, 32455, 125]

for cat_id in category_ids:
    result = get_fred_category(cat_id)
    data = json.loads(result)
    if "error" not in data:
        print(f"{data['data']['id']}: {data['data']['name']}")
```

**Result:** Quick overview of multiple categories.

---

## Use Cases

### 1. Category Tree Exploration

**Problem:** Need to understand FRED's organization structure.

**Solution:**
```python
# Start at root
root = get_fred_category(0)
print("Root:", json.loads(root)["data"]["name"])

# Explore top-level categories
top_level_ids = [32991, 32992, 3008, 32455]
for cat_id in top_level_ids:
    result = get_fred_category(cat_id)
    data = json.loads(result)
    print(f"- {data['data']['name']}")
```

**Benefits:**
- Understand FRED taxonomy
- Plan data exploration strategy
- Find relevant category branches

---

### 2. Navigate to Parent Categories

**Problem:** You have a specific category and want to see its broader context.

**Solution:**
```python
def navigate_to_root(category_id):
    """Navigate from category to root, printing path."""
    path = []
    current_id = category_id

    while True:
        result = get_fred_category(current_id)
        data = json.loads(result)

        if "error" in data:
            break

        cat = data["data"]
        path.append(f"{cat['name']} (ID: {cat['id']})")

        # Stop at root
        if cat["parent_id"] == 0 and cat["id"] == 0:
            break
        # Stop if we've reached root's child
        if cat["parent_id"] == 0:
            path.append("Categories (ID: 0)")
            break

        current_id = cat["parent_id"]

    return " > ".join(reversed(path))

# Example: Trade Balance category
print(navigate_to_root(125))
# Output: Categories > International Data > Trade Balance
```

**Benefits:**
- Understand category context
- See full hierarchical path
- Identify related categories

---

### 3. Validate Category Before Data Query

**Problem:** Want to verify category exists before querying its series.

**Solution:**
```python
def get_category_series(category_id):
    """Get series for a category, with validation."""
    # First, validate category exists
    cat_info = get_fred_category(category_id)
    cat_data = json.loads(cat_info)

    if "error" in cat_data:
        return f"Error: {cat_data['error']}"

    print(f"Category: {cat_data['data']['name']}")

    # Now safe to query series in this category
    # (would use category/series endpoint)
    return cat_data["data"]

result = get_category_series(125)
```

**Benefits:**
- Prevent errors
- Provide user feedback
- Validate user input

---

### 4. Build Category Breadcrumb

**Problem:** Show user where they are in category hierarchy.

**Solution:**
```python
def get_breadcrumb(category_id):
    """Generate breadcrumb navigation for category."""
    breadcrumb = []
    current_id = category_id

    # Navigate up to root
    while current_id is not None:
        result = get_fred_category(current_id)
        data = json.loads(result)

        if "error" in data:
            break

        cat = data["data"]
        breadcrumb.insert(0, {
            "id": cat["id"],
            "name": cat["name"]
        })

        if cat["id"] == 0:  # Reached root
            break

        current_id = cat["parent_id"] if cat["parent_id"] != cat["id"] else None

    return breadcrumb

# Example
crumbs = get_breadcrumb(125)
print(" > ".join([c["name"] for c in crumbs]))
```

**Benefits:**
- User-friendly navigation
- Show context
- Enable back-navigation

---

### 5. Category Metadata Caching

**Problem:** Repeatedly querying same categories wastes API calls.

**Solution:**
```python
category_cache = {}

def get_category_cached(category_id):
    """Get category with caching."""
    if category_id in category_cache:
        return category_cache[category_id]

    result = get_fred_category(category_id)
    data = json.loads(result)

    if "error" not in data:
        category_cache[category_id] = data

    return data

# Use cached version
for _ in range(10):
    data = get_category_cached(125)  # Only queries API once
```

**Benefits:**
- Reduce API calls
- Faster responses
- Stay under rate limits

---

## Category Tree Navigation

### Understanding the Hierarchy

```
Root (0: Categories)
├── 32991: Money, Banking, & Finance
│   ├── Child categories...
│   └── Series data...
├── 32992: National Accounts
│   ├── Child categories...
│   └── Series data...
├── 3008: Population, Employment, & Labor Markets
│   ├── Child categories...
│   └── Series data...
└── Other top-level categories...
```

### Navigation Patterns

#### Pattern 1: Top-Down Exploration
```python
# Start from root
root = get_fred_category(0)

# Get child categories (would use category/children)
# Navigate down to specific topics
```

#### Pattern 2: Bottom-Up Context
```python
# Start from specific category
specific = get_fred_category(125)

# Navigate to parent for context
parent_id = json.loads(specific)["data"]["parent_id"]
parent = get_fred_category(parent_id)
```

#### Pattern 3: Sibling Discovery
```python
# Get category's parent
cat = get_fred_category(125)
parent_id = json.loads(cat)["data"]["parent_id"]

# Get parent's children (would use category/children)
# Find sibling categories
```

---

## Common Categories

### Top-Level Categories (parent_id=0)

| ID | Name | Description |
|----|------|-------------|
| 0 | Categories | Root category |
| 32991 | Money, Banking, & Finance | Financial data, interest rates, credit |
| 32992 | National Accounts | GDP, GNP, national income accounts |
| 3008 | Population, Employment, & Labor Markets | Labor statistics, demographics |
| 32455 | Business Cycle Expansions & Contractions | Economic cycles, recessions |
| 32263 | Academic Data | Research and academic datasets |
| 1 | Production & Business Activity | Manufacturing, industrial production |
| 10 | Population, Employment, & Labor Markets | Employment data |
| 32348 | Prices | CPI, PPI, inflation data |
| 13 | International Data | Trade, exchange rates |

### Frequently Used Categories

| ID | Name | Parent | Use Case |
|----|------|--------|----------|
| 125 | Trade Balance | 13 | Import/export data |
| 106 | Housing | 1 | Real estate, construction |
| 33060 | Interest Rates | 32991 | Fed funds, treasury rates |
| 33596 | GDP/GNP | 32992 | Economic output |
| 12 | Foreign Exchange | 13 | Currency exchange rates |

---

## Error Handling

### Common Errors

#### Invalid Category ID

**Error:**
```json
{
  "tool": "get_category",
  "error": "Invalid parameters: Bad Request. The category does not exist.",
  "category_id": 999999999
}
```

**Cause:** Category ID doesn't exist in FRED

**Fix:**
```python
# Validate before using
result = get_fred_category(category_id)
data = json.loads(result)

if "error" in data:
    print(f"Category {category_id} not found")
    # Use fallback or prompt user
else:
    # Safe to use category
    process_category(data["data"])
```

---

#### Negative Category ID

**Error:**
```json
{
  "tool": "get_category",
  "error": "Invalid category_id: must be a non-negative integer"
}
```

**Cause:** Provided negative number

**Fix:**
```python
# Validate input
category_id = max(0, user_input)  # Ensure non-negative
result = get_fred_category(category_id)
```

---

#### Rate Limit Exceeded

**Error:**
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

**Cause:** Too many API requests

**Fix:**
```python
import time

def get_category_with_retry(category_id, max_retries=3):
    """Get category with retry on rate limit."""
    for attempt in range(max_retries):
        result = get_fred_category(category_id)
        data = json.loads(result)

        if "error" not in data or "rate limit" not in data["error"].lower():
            return data

        # Wait before retry
        time.sleep(2 ** attempt)  # Exponential backoff

    return data

result = get_category_with_retry(125)
```

---

## Performance

### Response Time

- **Typical:** 0.26-0.52 seconds
- **Root category:** ~0.5s
- **Cached categories:** Instant (if implementing caching)
- **With errors:** 4+ seconds (includes retries)

### Optimization Tips

1. **Cache frequently used categories:**
```python
COMMON_CATEGORIES = {
    0: None,     # Root
    32991: None, # Money, Banking
    32992: None, # National Accounts
}

# Pre-load on startup
for cat_id in COMMON_CATEGORIES:
    result = get_fred_category(cat_id)
    COMMON_CATEGORIES[cat_id] = json.loads(result)
```

2. **Batch lookups strategically:**
```python
# Don't query one at a time in loop
# Query all needed categories upfront
needed_ids = [125, 32991, 32992]
categories = {
    cat_id: json.loads(get_fred_category(cat_id))
    for cat_id in needed_ids
}
```

3. **Validate before querying:**
```python
# Check if ID looks valid before API call
if category_id < 0:
    return {"error": "Invalid ID"}

result = get_fred_category(category_id)
```

### Token Efficiency

**Typical response sizes:**
- Minimal category: ~200 tokens
- Category with notes: ~300 tokens
- With metadata: ~250 tokens average

**Very token-efficient** - good for AI/LLM applications.

---

## Best Practices

### 1. Always Handle Errors

```python
# Good - error handling
result = get_fred_category(category_id)
data = json.loads(result)

if "error" in data:
    logger.error(f"Category error: {data['error']}")
    return None

return data["data"]

# Bad - no error handling
data = json.loads(get_fred_category(category_id))
return data["data"]  # May crash if error present
```

### 2. Cache Category Metadata

```python
# Good - cache for repeated access
from functools import lru_cache

@lru_cache(maxsize=128)
def get_category_cached(category_id):
    return get_fred_category(category_id)

# Use cached version
for i in range(100):
    data = get_category_cached(125)  # Only queries once
```

### 3. Validate User Input

```python
# Good - validate before API call
def safe_get_category(category_id):
    try:
        cat_id = int(category_id)
        if cat_id < 0:
            return {"error": "Category ID must be non-negative"}
        return get_fred_category(cat_id)
    except ValueError:
        return {"error": "Category ID must be an integer"}

# Bad - no validation
result = get_fred_category(user_input)  # May crash
```

### 4. Build Navigation Helpers

```python
# Good - reusable navigation function
def get_category_path(category_id):
    """Get full path from root to category."""
    path = []
    current = category_id

    while current is not None:
        result = get_fred_category(current)
        data = json.loads(result)

        if "error" in data:
            break

        path.insert(0, data["data"])
        parent = data["data"]["parent_id"]

        if parent == current:  # Root
            break
        current = parent

    return path
```

### 5. Use Descriptive Logging

```python
# Good - informative logs
import logging

logger = logging.getLogger(__name__)

result = get_fred_category(125)
data = json.loads(result)

if "error" not in data:
    logger.info(
        f"Retrieved category: {data['data']['name']} "
        f"(ID: {data['data']['id']}, Parent: {data['data']['parent_id']})"
    )
```

---

## Related Tools

### Complementary Tools

1. **`category/children`** (Future)
   - Get child categories of a category
   - Explore category tree downward
   - **Use AFTER** `get_fred_category` to explore children

2. **`category/series`** (Future)
   - Get series in a category
   - Retrieve actual data series
   - **Use AFTER** `get_fred_category` to get category's data

3. **`search_fred_series`**
   - Search for series
   - Can filter by category
   - **Use WITH** category_id parameter

4. **`get_fred_series_tags`**
   - Get tags for a series
   - Understand series categorization
   - **Use AFTER** finding series in category

### Typical Workflow

```python
# Step 1: Explore categories
root = get_fred_category(0)
print(f"Root: {json.loads(root)['data']['name']}")

# Step 2: Navigate to topic of interest
money = get_fred_category(32991)
print(f"Topic: {json.loads(money)['data']['name']}")

# Step 3: Get child categories (future: category/children)
# children = get_category_children(32991)

# Step 4: Get series in category (future: category/series)
# series = get_category_series(32991)

# Step 5: Get observations for specific series
# data = get_fred_series_observations("DFF")
```

---

## Version Information

- **Tool Version:** Introduced in v0.1.8 (planned)
- **FRED API Version:** Uses FRED API `/fred/category` endpoint
- **Last Updated:** 2025-11-01

---

## Support & Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/fred/
- **Endpoint Docs:** https://fred.stlouisfed.org/docs/api/fred/category.html
- **FRED Categories:** https://fred.stlouisfed.org/categories
- **FRED Homepage:** https://fred.stlouisfed.org/

---

## Summary

The `get_fred_category` tool is essential for:

✅ **Understanding FRED organization** - See how data is categorized
✅ **Category navigation** - Explore taxonomy tree structure
✅ **Data discovery** - Find categories containing relevant data
✅ **Context building** - Understand category relationships
✅ **Validation** - Verify category IDs before queries

**Key Strengths:**
- Simple, focused API
- Fast responses (< 0.5s)
- Clear hierarchy information
- Enables tree navigation
- AI-optimized compact JSON

**Best For:**
- Exploring FRED taxonomy
- Building category navigation
- Understanding data organization
- Validating category IDs
- Creating breadcrumb trails

**Remember:**
- Root category is always ID=0
- Use parent_id to navigate up
- Check for errors before using data
- Cache frequently accessed categories
- Top-level categories have parent_id=0

**Perfect First Step** for discovering and organizing FRED economic data!
