# FRED Category Children Tool - Complete API Reference

## Overview

The `get_category_children` tool retrieves all direct child categories for a specified parent category in FRED's hierarchical taxonomy. This tool is essential for top-down exploration of the category tree, enabling discovery of sub-categories within any topic area.

**Tool Name**: `get_category_children`
**MCP Tool ID**: `get_fred_category_children`
**FRED API Endpoint**: `https://api.stlouisfed.org/fred/category/children`
**Purpose**: Hierarchical category tree navigation and discovery

---

## Table of Contents

1. [Parameters](#parameters)
2. [Response Format](#response-format)
3. [Usage Examples](#usage-examples)
4. [Common Use Cases](#common-use-cases)
5. [Navigation Patterns](#navigation-patterns)
6. [Category Tree Structure](#category-tree-structure)
7. [Best Practices](#best-practices)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Integration with Other Tools](#integration-with-other-tools)
11. [API Reference](#api-reference)

---

## Parameters

### Required Parameters

None - all parameters are optional. Calling with no parameters returns top-level categories.

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category_id` | `int` | `0` | The ID for a parent category. `0` returns root/top-level categories |
| `realtime_start` | `str` | Today | Start date for real-time period (YYYY-MM-DD format) |
| `realtime_end` | `str` | Today | End date for real-time period (YYYY-MM-DD format) |

### Parameter Details

#### `category_id`
- **Type**: Non-negative integer
- **Default**: `0` (root category)
- **Range**: 0 to maximum category ID
- **Validation**: Must be ≥ 0
- **Special Values**:
  - `0`: Returns top-level categories (Production, Employment, National Accounts, etc.)
  - Any valid category ID: Returns its direct children

**Common Parent Categories**:
| ID | Name | Description |
|----|------|-------------|
| 0 | Root | Returns 8 top-level categories |
| 13 | International Data | Trade, exchange rates, imports/exports |
| 32991 | Money, Banking, & Finance | Interest rates, monetary data, exchange rates |
| 10 | Population, Employment, & Labor Markets | Employment, unemployment, labor force |
| 32992 | National Accounts | GDP, consumption, investment, government spending |
| 1 | Production & Business Activity | Industrial production, capacity utilization |
| 32455 | Prices | Inflation, CPI, PPI, deflators |

#### `realtime_start` and `realtime_end`
- **Type**: String in YYYY-MM-DD format
- **Default**: Today's date
- **Purpose**: Specify the real-time period for category structure
- **Use Case**: View historical category organization
- **Note**: Category structures rarely change, so these parameters are infrequently used

---

## Response Format

### Success Response Structure

```json
{
  "tool": "get_category_children",
  "data": [
    {
      "id": 16,
      "name": "Exports",
      "parent_id": 13
    },
    {
      "id": 17,
      "name": "Imports",
      "parent_id": 13,
      "notes": "Optional category description"
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "parent_category_id": 13,
    "total_count": 6,
    "returned_count": 6,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### Data Array (Child Categories)
Each child category object contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Unique category identifier |
| `name` | `str` | Category display name |
| `parent_id` | `int` | Parent category ID (matches request parameter) |
| `notes` | `str` | Optional category description (not always present) |

#### Metadata Object

| Field | Type | Description |
|-------|------|-------------|
| `fetch_date` | `str` | ISO 8601 timestamp of when data was retrieved |
| `parent_category_id` | `int` | The parent category ID that was queried |
| `total_count` | `int` | Total number of child categories |
| `returned_count` | `int` | Number of categories returned (same as total_count) |
| `realtime_start` | `str` | Real-time period start date |
| `realtime_end` | `str` | Real-time period end date |

### Empty Response (Leaf Category)

When querying a leaf category (no children):

```json
{
  "tool": "get_category_children",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "parent_category_id": 125,
    "total_count": 0,
    "returned_count": 0,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Error Response Structure

```json
{
  "tool": "get_category_children",
  "error": "Category not found: 999999",
  "category_id": 999999
}
```

**Common Error Messages**:
- `"Invalid category_id: must be a non-negative integer"` - Negative or invalid category_id
- `"Category not found: {id}"` - Invalid category ID (404)
- `"Invalid parameters: {detail}"` - Bad request parameters (400)
- `"Rate limit exceeded. Please try again later."` - Too many requests (429)
- `"Unexpected error: {message}"` - Server or network error

---

## Usage Examples

### Example 1: Get Top-Level Categories

Discover all top-level categories in FRED's taxonomy:

```python
# Get root categories
result = get_category_children(0)
```

**Response**:
```json
{
  "tool": "get_category_children",
  "data": [
    {"id": 32991, "name": "Money, Banking, & Finance", "parent_id": 0},
    {"id": 10, "name": "Population, Employment, & Labor Markets", "parent_id": 0},
    {"id": 32992, "name": "National Accounts", "parent_id": 0},
    {"id": 1, "name": "Production & Business Activity", "parent_id": 0},
    {"id": 32455, "name": "Prices", "parent_id": 0},
    {"id": 33060, "name": "U.S. Regional Data", "parent_id": 0},
    {"id": 3008, "name": "Academic Data", "parent_id": 0},
    {"id": 13, "name": "International Data", "parent_id": 0}
  ],
  "metadata": {
    "parent_category_id": 0,
    "total_count": 8
  }
}
```

**Use Case**: Building a category browser, showing main topic areas.

---

### Example 2: Explore International Data Subcategories

Navigate into the International Data category:

```python
# Get children of International Data (ID: 13)
result = get_category_children(13)
```

**Response**:
```json
{
  "tool": "get_category_children",
  "data": [
    {"id": 16, "name": "Exports", "parent_id": 13},
    {"id": 17, "name": "Imports", "parent_id": 13},
    {"id": 3000, "name": "Income Payments & Receipts", "parent_id": 13},
    {"id": 125, "name": "Trade Balance", "parent_id": 13},
    {"id": 193, "name": "U.S. Trade & International Transactions", "parent_id": 13},
    {"id": 15, "name": "Exchange Rates", "parent_id": 13}
  ],
  "metadata": {
    "parent_category_id": 13,
    "total_count": 6
  }
}
```

**Use Case**: Drilling down into specific topic areas to find relevant data series.

---

### Example 3: Navigate Money, Banking, & Finance

Explore financial data categories:

```python
# Get children of Money, Banking, & Finance (ID: 32991)
result = get_category_children(32991)
```

**Response**:
```json
{
  "tool": "get_category_children",
  "data": [
    {"id": 22, "name": "Interest Rates", "parent_id": 32991},
    {"id": 15, "name": "Exchange Rates", "parent_id": 32991},
    {"id": 24, "name": "Monetary Data", "parent_id": 32991},
    {"id": 32348, "name": "Banking", "parent_id": 32991},
    {"id": 33491, "name": "Finance Companies", "parent_id": 32991},
    {"id": 33493, "name": "Insurance", "parent_id": 32991},
    {"id": 33492, "name": "Securities", "parent_id": 32991}
  ],
  "metadata": {
    "parent_category_id": 32991,
    "total_count": 7
  }
}
```

**Use Case**: Finding interest rate, monetary policy, or banking data.

---

### Example 4: Identify Leaf Categories

Check if a category has children (determines if it's a leaf node):

```python
# Check if Trade Balance (ID: 125) has children
result = get_category_children(125)
```

**Response**:
```json
{
  "tool": "get_category_children",
  "data": [],
  "metadata": {
    "parent_category_id": 125,
    "total_count": 0
  }
}
```

**Interpretation**:
- `total_count: 0` indicates this is a **leaf category**
- Leaf categories contain data series but no subcategories
- Use `search_fred_series` or category/series endpoint to find series in this category

---

### Example 5: Multi-Level Navigation

Build a complete navigation path from root to specific topic:

```python
# Step 1: Get top-level categories
root = get_category_children(0)
# Identify "International Data" (ID: 13)

# Step 2: Get International Data children
intl = get_category_children(13)
# Identify "Trade Balance" (ID: 125)

# Step 3: Check if Trade Balance has children
trade = get_category_children(125)
# Result: Empty (leaf category)

# Step 4: Get series in Trade Balance category
# Use get_category_series(125) or search_fred_series with filters
```

**Navigation Path**: Root → International Data → Trade Balance

---

### Example 6: Building Category Trees

Recursively build a complete category tree:

```python
def build_category_tree(parent_id=0, max_depth=3, current_depth=0):
    """Recursively build category tree."""
    if current_depth >= max_depth:
        return None

    result = get_category_children(parent_id)
    children_data = json.loads(result)

    tree = {
        "category_id": parent_id,
        "children": []
    }

    for child in children_data["data"]:
        child_node = {
            "id": child["id"],
            "name": child["name"],
            "subtree": build_category_tree(
                child["id"],
                max_depth,
                current_depth + 1
            )
        }
        tree["children"].append(child_node)

    return tree

# Build 3-level tree from root
full_tree = build_category_tree(0, max_depth=3)
```

**Use Case**: Creating visual category explorers, documentation, or navigation UI.

---

### Example 7: Historical Category Structure

View category organization from a specific date:

```python
# View category children as they existed on Jan 1, 2020
result = get_category_children(
    category_id=13,
    realtime_start="2020-01-01",
    realtime_end="2020-01-01"
)
```

**Note**: Category structures rarely change, so this is mainly for auditing or historical research.

---

## Common Use Cases

### Use Case 1: Category Explorer / Navigation UI

**Scenario**: Build an interactive category browser for users to explore FRED data.

**Implementation**:
```python
def explore_categories_interactive():
    """Interactive category explorer."""
    current_id = 0  # Start at root
    breadcrumb = [(0, "Root")]

    while True:
        # Get children of current category
        result = get_category_children(current_id)
        data = json.loads(result)

        # Display current location
        path = " → ".join([name for _, name in breadcrumb])
        print(f"\nCurrent path: {path}")
        print(f"Found {len(data['data'])} subcategories:\n")

        # Display children
        for i, child in enumerate(data['data'], 1):
            print(f"{i}. {child['name']} (ID: {child['id']})")

        # Navigation options
        print("\nOptions:")
        print("- Enter number to explore subcategory")
        print("- Enter 'b' to go back")
        print("- Enter 'q' to quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == 'b' and len(breadcrumb) > 1:
            breadcrumb.pop()
            current_id = breadcrumb[-1][0]
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(data['data']):
                child = data['data'][idx]
                current_id = child['id']
                breadcrumb.append((child['id'], child['name']))
```

**Benefits**:
- User-friendly navigation
- Visual breadcrumb trail
- Quick exploration of FRED's organization

---

### Use Case 2: Automated Category Discovery

**Scenario**: Automatically map all categories in a specific domain (e.g., all employment-related categories).

**Implementation**:
```python
def find_categories_by_keyword(keyword, start_id=0, max_depth=4):
    """Find all categories matching a keyword."""
    matches = []

    def search_recursive(parent_id, depth=0, path=[]):
        if depth > max_depth:
            return

        result = get_category_children(parent_id)
        data = json.loads(result)

        for child in data['data']:
            current_path = path + [child['name']]

            # Check if keyword matches
            if keyword.lower() in child['name'].lower():
                matches.append({
                    'id': child['id'],
                    'name': child['name'],
                    'path': ' → '.join(current_path),
                    'depth': depth + 1
                })

            # Recurse into children
            search_recursive(child['id'], depth + 1, current_path)

    search_recursive(start_id)
    return matches

# Find all employment-related categories
employment_cats = find_categories_by_keyword("employment")
for cat in employment_cats:
    print(f"{cat['name']} (ID: {cat['id']})")
    print(f"  Path: {cat['path']}\n")
```

**Results**:
```
Population, Employment, & Labor Markets (ID: 10)
  Path: Population, Employment, & Labor Markets

Employment Cost Index (ID: 4)
  Path: Production & Business Activity → Employment Cost Index
```

---

### Use Case 3: Category Validation Pipeline

**Scenario**: Validate that specific categories exist before running data retrieval workflows.

**Implementation**:
```python
def validate_category_path(category_ids):
    """Validate a sequence of parent→child relationships."""
    for i in range(len(category_ids) - 1):
        parent_id = category_ids[i]
        expected_child_id = category_ids[i + 1]

        # Get children
        result = get_category_children(parent_id)
        data = json.loads(result)

        # Check if expected child exists
        child_ids = [c['id'] for c in data['data']]

        if expected_child_id not in child_ids:
            return False, f"Category {expected_child_id} not a child of {parent_id}"

    return True, "Valid path"

# Validate: Root → International Data → Trade Balance
is_valid, message = validate_category_path([0, 13, 125])
print(f"Path valid: {is_valid} - {message}")
```

**Use Case**: Data pipeline integrity checks, configuration validation.

---

### Use Case 4: Category Comparison Across Time

**Scenario**: Compare category structures between two time periods to detect changes.

**Implementation**:
```python
def compare_category_structure(category_id, date1, date2):
    """Compare category children at two different dates."""
    # Get children at date 1
    result1 = get_category_children(
        category_id,
        realtime_start=date1,
        realtime_end=date1
    )
    data1 = json.loads(result1)

    # Get children at date 2
    result2 = get_category_children(
        category_id,
        realtime_start=date2,
        realtime_end=date2
    )
    data2 = json.loads(result2)

    # Compare
    ids1 = {c['id']: c['name'] for c in data1['data']}
    ids2 = {c['id']: c['name'] for c in data2['data']}

    added = set(ids2.keys()) - set(ids1.keys())
    removed = set(ids1.keys()) - set(ids2.keys())

    print(f"Category {category_id} changes from {date1} to {date2}:")
    print(f"Added: {len(added)} categories")
    print(f"Removed: {len(removed)} categories")

    if added:
        print("\nNew categories:")
        for cat_id in added:
            print(f"  - {ids2[cat_id]} (ID: {cat_id})")

    if removed:
        print("\nRemoved categories:")
        for cat_id in removed:
            print(f"  - {ids1[cat_id]} (ID: {cat_id})")

# Compare International Data category structure
compare_category_structure(13, "2015-01-01", "2025-01-01")
```

---

### Use Case 5: Generate Category Documentation

**Scenario**: Automatically generate documentation of FRED's category hierarchy.

**Implementation**:
```python
def generate_category_docs(parent_id=0, max_depth=3):
    """Generate markdown documentation of category tree."""
    def document_recursive(cat_id, depth=0, output=[]):
        if depth > max_depth:
            return

        # Get category info
        cat_result = get_category(cat_id)
        cat_data = json.loads(cat_result)['data']

        # Get children
        children_result = get_category_children(cat_id)
        children_data = json.loads(children_result)

        # Format entry
        indent = "  " * depth
        if depth == 0:
            output.append(f"# FRED Category Structure\n")
        else:
            output.append(f"{indent}- **{cat_data['name']}** (ID: {cat_id})")

        # Add child count
        child_count = len(children_data['data'])
        if child_count > 0:
            output.append(f"{indent}  - {child_count} subcategories")
        else:
            output.append(f"{indent}  - Leaf category (contains series)")

        # Recurse
        for child in children_data['data']:
            document_recursive(child['id'], depth + 1, output)

        return output

    lines = document_recursive(parent_id)
    return "\n".join(lines)

# Generate docs for International Data
docs = generate_category_docs(13, max_depth=2)
print(docs)
```

**Output**:
```markdown
# FRED Category Structure
- **International Data** (ID: 13)
  - 6 subcategories
  - **Exports** (ID: 16)
    - Leaf category (contains series)
  - **Imports** (ID: 17)
    - Leaf category (contains series)
  ...
```

---

## Navigation Patterns

### Pattern 1: Top-Down Exploration

Start from root and drill down to specific topics:

```
Root (0)
  ├─ Money, Banking, & Finance (32991)
  │   ├─ Interest Rates (22)
  │   │   ├─ Fed Funds Rate series
  │   │   └─ Treasury Rates series
  │   └─ Monetary Data (24)
  │
  ├─ National Accounts (32992)
  │   ├─ GDP series
  │   └─ Consumption series
  └─ ...
```

**Steps**:
1. `get_category_children(0)` → Get top-level categories
2. Select category → `get_category_children(32991)`
3. Continue drilling → `get_category_children(22)`
4. Retrieve series → `search_fred_series` or category/series

---

### Pattern 2: Bottom-Up Navigation

Start from a known series, navigate up to parent categories:

```python
# Step 1: Get series info to find its category
series_info = get_series_observations("GDP")
# (Series info would include category_id)

# Step 2: Get category info
category = get_category(106)  # GDP category

# Step 3: Get parent
parent_id = json.loads(category)['data']['parent_id']
parent = get_category(parent_id)

# Step 4: Get siblings (other children of parent)
siblings = get_category_children(parent_id)
```

---

### Pattern 3: Breadth-First Traversal

Explore all categories at each level before going deeper:

```python
from collections import deque

def breadth_first_traversal(root_id=0, max_levels=3):
    """BFS traversal of category tree."""
    queue = deque([(root_id, 0)])  # (category_id, level)
    visited = set()

    while queue:
        cat_id, level = queue.popleft()

        if cat_id in visited or level > max_levels:
            continue

        visited.add(cat_id)

        # Process current category
        cat_info = get_category(cat_id)
        cat_data = json.loads(cat_info)['data']
        print(f"{'  ' * level}Level {level}: {cat_data['name']} (ID: {cat_id})")

        # Get children and add to queue
        children_result = get_category_children(cat_id)
        children_data = json.loads(children_result)

        for child in children_data['data']:
            queue.append((child['id'], level + 1))

# Explore first 3 levels
breadth_first_traversal(0, max_levels=3)
```

---

### Pattern 4: Leaf Category Detection

Identify categories that contain series (no children):

```python
def find_all_leaf_categories(parent_id=0, max_depth=5):
    """Find all leaf categories (categories with no children)."""
    leaves = []

    def traverse(cat_id, depth=0, path=[]):
        if depth > max_depth:
            return

        # Get category info
        cat_result = get_category(cat_id)
        cat_data = json.loads(cat_result)['data']

        # Get children
        children_result = get_category_children(cat_id)
        children_data = json.loads(children_result)

        current_path = path + [cat_data['name']]

        # Check if leaf
        if len(children_data['data']) == 0:
            leaves.append({
                'id': cat_id,
                'name': cat_data['name'],
                'path': ' → '.join(current_path),
                'parent_id': cat_data.get('parent_id')
            })
        else:
            # Recurse into children
            for child in children_data['data']:
                traverse(child['id'], depth + 1, current_path)

    traverse(parent_id)
    return leaves

# Find all leaf categories under International Data
leaves = find_all_leaf_categories(13, max_depth=3)
print(f"Found {len(leaves)} leaf categories:")
for leaf in leaves[:5]:  # Show first 5
    print(f"  {leaf['name']} (ID: {leaf['id']})")
    print(f"    Path: {leaf['path']}\n")
```

---

## Category Tree Structure

### FRED Top-Level Categories (Level 0)

Calling `get_category_children(0)` returns these 8 top-level categories:

| ID | Name | Description | Typical Children |
|----|------|-------------|------------------|
| 32991 | Money, Banking, & Finance | Financial and monetary data | Interest Rates, Exchange Rates, Monetary Data, Banking |
| 10 | Population, Employment, & Labor Markets | Labor force statistics | Unemployment, Employment, Labor Force Participation |
| 32992 | National Accounts | GDP and economic accounts | GDP, Consumption, Investment, Government Spending |
| 1 | Production & Business Activity | Output and business metrics | Industrial Production, Capacity Utilization, Retail |
| 32455 | Prices | Inflation and price indices | CPI, PPI, PCE, Import/Export Prices |
| 33060 | U.S. Regional Data | State and MSA data | State-level series, Metropolitan data |
| 3008 | Academic Data | Research and educational data | Special datasets, Research series |
| 13 | International Data | Cross-border economic data | Trade, Exchange Rates, International Transactions |

### Tree Depth Characteristics

- **Average Depth**: 3-4 levels from root to leaf categories
- **Maximum Depth**: ~5-6 levels in some branches
- **Leaf Categories**: ~300-400 categories that directly contain series
- **Total Categories**: ~500-600 total categories in the tree

### Example: Money, Banking, & Finance Branch

```
Money, Banking, & Finance (32991)
├── Interest Rates (22)
│   ├── Commercial Bank Rates
│   ├── Treasury Rates
│   ├── Mortgage Rates
│   └── Corporate Bond Rates
├── Exchange Rates (15)
│   ├── Bilateral Rates
│   └── Effective Rates
├── Monetary Data (24)
│   ├── M1, M2 Aggregates
│   ├── Reserves
│   └── Currency in Circulation
├── Banking (32348)
│   ├── Bank Assets
│   ├── Bank Liabilities
│   └── Credit Conditions
└── ...
```

---

## Best Practices

### 1. Start Exploration from Root

Always begin category exploration from the root:

```python
# GOOD: Start from root
top_level = get_category_children(0)

# Then drill down based on results
children = get_category_children(specific_id)
```

### 2. Cache Category Structure

Category structures change infrequently - cache results:

```python
import json
from datetime import datetime, timedelta

class CategoryCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)

    def get_children(self, category_id):
        cache_key = f"children_{category_id}"

        # Check cache
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                return data

        # Fetch fresh data
        result = get_category_children(category_id)
        self.cache[cache_key] = (result, datetime.now())
        return result

# Use cached version
cache = CategoryCache(ttl_hours=24)
result = cache.get_children(13)
```

**Benefits**:
- Reduces API calls
- Faster response times
- Respects rate limits

### 3. Implement Depth Limits

Prevent infinite recursion when traversing:

```python
def safe_traverse(category_id, max_depth=5, current_depth=0):
    """Safely traverse with depth limit."""
    if current_depth >= max_depth:
        print(f"Max depth {max_depth} reached")
        return

    result = get_category_children(category_id)
    data = json.loads(result)

    for child in data['data']:
        # Process child
        safe_traverse(child['id'], max_depth, current_depth + 1)
```

### 4. Handle Empty Results Gracefully

Check for leaf categories:

```python
result = get_category_children(category_id)
data = json.loads(result)

if len(data['data']) == 0:
    print(f"Category {category_id} is a leaf - no children")
    print("Use search_fred_series or category/series to find series")
else:
    print(f"Found {len(data['data'])} child categories")
```

### 5. Build Navigation Breadcrumbs

Track user's path for better UX:

```python
class CategoryNavigator:
    def __init__(self):
        self.breadcrumb = [(0, "Root")]

    def navigate_to(self, category_id, category_name):
        """Navigate to a child category."""
        self.breadcrumb.append((category_id, category_name))

    def go_back(self):
        """Go back to parent."""
        if len(self.breadcrumb) > 1:
            self.breadcrumb.pop()

    def get_current(self):
        """Get current category ID."""
        return self.breadcrumb[-1][0]

    def get_path(self):
        """Get breadcrumb path."""
        return " → ".join([name for _, name in self.breadcrumb])

nav = CategoryNavigator()
print(nav.get_path())  # "Root"

nav.navigate_to(13, "International Data")
print(nav.get_path())  # "Root → International Data"

nav.navigate_to(125, "Trade Balance")
print(nav.get_path())  # "Root → International Data → Trade Balance"

nav.go_back()
print(nav.get_path())  # "Root → International Data"
```

### 6. Combine with get_category for Full Context

Use both tools together:

```python
def get_full_category_info(category_id):
    """Get complete category information."""
    # Get category metadata
    cat_result = get_category(category_id)
    cat_data = json.loads(cat_result)['data']

    # Get children
    children_result = get_category_children(category_id)
    children_data = json.loads(children_result)

    # Get parent info (if not root)
    parent_info = None
    if cat_data.get('parent_id') is not None:
        parent_result = get_category(cat_data['parent_id'])
        parent_info = json.loads(parent_result)['data']

    return {
        'current': cat_data,
        'parent': parent_info,
        'children': children_data['data'],
        'is_leaf': len(children_data['data']) == 0
    }

info = get_full_category_info(125)
print(f"Current: {info['current']['name']}")
print(f"Parent: {info['parent']['name'] if info['parent'] else 'None'}")
print(f"Children: {len(info['children'])}")
print(f"Is Leaf: {info['is_leaf']}")
```

### 7. Batch Category Lookups

When exploring multiple categories, batch your requests:

```python
import time

def batch_get_children(category_ids, delay=0.1):
    """Get children for multiple categories with rate limiting."""
    results = {}

    for cat_id in category_ids:
        result = get_category_children(cat_id)
        results[cat_id] = json.loads(result)

        # Rate limiting
        if delay > 0:
            time.sleep(delay)

    return results

# Get children for multiple categories
categories = [13, 32991, 10]  # International, Money/Banking, Employment
all_children = batch_get_children(categories)

for cat_id, data in all_children.items():
    print(f"Category {cat_id}: {len(data['data'])} children")
```

---

## Error Handling

### Common Errors and Solutions

#### 1. Invalid Category ID

**Error**: `"Invalid category_id: must be a non-negative integer"`

**Cause**: Negative category_id or non-integer value

**Solution**:
```python
def safe_get_children(category_id):
    """Safely get children with validation."""
    if not isinstance(category_id, int) or category_id < 0:
        print(f"Invalid category_id: {category_id}")
        return None

    result = get_category_children(category_id)
    data = json.loads(result)

    if 'error' in data:
        print(f"Error: {data['error']}")
        return None

    return data

# Safe usage
result = safe_get_children(13)
if result:
    print(f"Found {len(result['data'])} children")
```

#### 2. Category Not Found

**Error**: `"Category not found: {id}"` (HTTP 404)

**Cause**: Category ID doesn't exist in FRED

**Solution**:
```python
def get_children_with_fallback(category_id, fallback_id=0):
    """Get children with fallback to parent or root."""
    result = get_category_children(category_id)
    data = json.loads(result)

    if 'error' in data and 'not found' in data['error'].lower():
        print(f"Category {category_id} not found, trying fallback {fallback_id}")
        result = get_category_children(fallback_id)
        data = json.loads(result)

    return data
```

#### 3. Rate Limit Exceeded

**Error**: `"Rate limit exceeded. Please try again later."` (HTTP 429)

**Cause**: Too many requests in short time period

**Solution**:
```python
import time

def get_children_with_retry(category_id, max_retries=3):
    """Get children with exponential backoff retry."""
    for attempt in range(max_retries):
        result = get_category_children(category_id)
        data = json.loads(result)

        if 'error' in data and 'rate limit' in data['error'].lower():
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        return data

    print("Max retries exceeded")
    return None
```

#### 4. Network Errors

**Error**: `"Unexpected error: {message}"`

**Cause**: Network issues, API downtime, timeout

**Solution**:
```python
def robust_get_children(category_id):
    """Get children with comprehensive error handling."""
    try:
        result = get_category_children(category_id)
        data = json.loads(result)

        # Check for API errors
        if 'error' in data:
            error_msg = data['error']

            if 'not found' in error_msg.lower():
                return {'status': 'not_found', 'data': None}
            elif 'rate limit' in error_msg.lower():
                return {'status': 'rate_limited', 'data': None}
            else:
                return {'status': 'error', 'message': error_msg, 'data': None}

        return {'status': 'success', 'data': data}

    except json.JSONDecodeError:
        return {'status': 'json_error', 'data': None}
    except Exception as e:
        return {'status': 'unexpected', 'message': str(e), 'data': None}

# Usage
result = robust_get_children(13)
if result['status'] == 'success':
    print(f"Found {len(result['data']['data'])} children")
else:
    print(f"Error: {result['status']}")
```

---

## Performance Considerations

### API Call Efficiency

**Single Category Query**:
- Average response time: 0.3-2.0 seconds
- Factors: Category size, network latency, API load

**Optimization Strategies**:

1. **Cache Aggressively**: Category structures rarely change
2. **Batch Related Queries**: Group category lookups together
3. **Use Depth Limits**: Prevent excessive recursion
4. **Implement Rate Limiting**: Respect API rate limits (default: 120 requests/minute)

### Response Size

- **Typical Response**: 0.5-5 KB
- **Large Categories**: Up to 10-15 KB (many children)
- **Empty Categories**: ~200 bytes

**Example Response Sizes**:
```
Root (0): ~2 KB (8 children)
International Data (13): ~1.5 KB (6 children)
Trade Balance (125): ~200 bytes (0 children)
```

### Rate Limits

FRED API rate limits:
- **Default**: 120 requests per minute (2 per second)
- **Burst**: Can exceed briefly, but sustained high rates trigger 429 errors

**Rate Limit Management**:
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_per_minute=100):
        self.max_per_minute = max_per_minute
        self.calls = deque()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove calls older than 1 minute
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()

        # Check if at limit
        if len(self.calls) >= self.max_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls.append(now)

# Use with category queries
limiter = RateLimiter(max_per_minute=100)

def rate_limited_get_children(category_id):
    limiter.wait_if_needed()
    return get_category_children(category_id)
```

---

## Integration with Other Tools

### 1. Combine with get_category

Navigate up and down the tree:

```python
# Get category info (navigate up via parent_id)
category = get_category(125)
parent_id = json.loads(category)['data']['parent_id']

# Get siblings (children of parent)
siblings = get_category_children(parent_id)

# Get own children (navigate down)
children = get_category_children(125)
```

### 2. Feed into search_fred_series

Use category discovery to refine series searches:

```python
# Step 1: Find relevant category
children = get_category_children(13)  # International Data
data = json.loads(children)

# Find Trade Balance category
trade_cat = next(c for c in data['data'] if 'Trade' in c['name'])
print(f"Found: {trade_cat['name']} (ID: {trade_cat['id']})")

# Step 2: Search for series in that category
# (Would use category/series endpoint or filtered search)
```

### 3. Build Complete Category Profiles

Combine multiple tools for comprehensive info:

```python
def get_complete_profile(category_id):
    """Get complete category profile."""
    # Basic info
    cat_result = get_category(category_id)
    cat_data = json.loads(cat_result)['data']

    # Children
    children_result = get_category_children(category_id)
    children_data = json.loads(children_result)

    # Parent (if exists)
    parent_data = None
    if cat_data.get('parent_id') is not None:
        parent_result = get_category(cat_data['parent_id'])
        parent_data = json.loads(parent_result)['data']

    # Siblings (if has parent)
    siblings_data = []
    if parent_data:
        siblings_result = get_category_children(parent_data['id'])
        siblings_data = json.loads(siblings_result)['data']

    return {
        'category': cat_data,
        'parent': parent_data,
        'children': children_data['data'],
        'siblings': siblings_data,
        'child_count': len(children_data['data']),
        'sibling_count': len(siblings_data) - 1,  # Exclude self
        'is_leaf': len(children_data['data']) == 0,
        'is_root': cat_data.get('parent_id') is None
    }

profile = get_complete_profile(125)
print(f"Category: {profile['category']['name']}")
print(f"Parent: {profile['parent']['name'] if profile['parent'] else 'None'}")
print(f"Children: {profile['child_count']}")
print(f"Siblings: {profile['sibling_count']}")
print(f"Type: {'Leaf' if profile['is_leaf'] else 'Branch'}")
```

### 4. Category-Series Workflow

Complete workflow from category to series data:

```python
def explore_and_retrieve_data(start_category=0):
    """Complete workflow: category → series → data."""

    # Step 1: Explore categories
    children = get_category_children(start_category)
    data = json.loads(children)

    print(f"Found {len(data['data'])} categories")
    for child in data['data']:
        print(f"  - {child['name']} (ID: {child['id']})")

    # Step 2: Select category (example: first child)
    selected = data['data'][0]
    print(f"\nSelected: {selected['name']}")

    # Step 3: Check if leaf
    sub_children = get_category_children(selected['id'])
    sub_data = json.loads(sub_children)

    if len(sub_data['data']) == 0:
        print("This is a leaf category - contains series")

        # Step 4: Search for series (would use search_fred_series)
        print("\nNext step: Use search_fred_series or category/series")
    else:
        print(f"Has {len(sub_data['data'])} subcategories - continue drilling")
```

---

## API Reference

### Function Signature

```python
def get_category_children(
    category_id: int = 0,
    realtime_start: Optional[str] = None,
    realtime_end: Optional[str] = None,
) -> str:
    """
    Get the child categories for a specified parent category.

    Args:
        category_id: Parent category ID (default: 0 for root)
        realtime_start: Real-time period start date (YYYY-MM-DD)
        realtime_end: Real-time period end date (YYYY-MM-DD)

    Returns:
        JSON string with child categories and metadata

    Raises:
        No exceptions raised - errors returned in JSON format
    """
```

### MCP Tool Schema

```json
{
  "name": "get_fred_category_children",
  "description": "Get the child categories for a specified parent category. Use this to navigate down the FRED category tree and discover subcategories within a topic area.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category_id": {
        "type": "integer",
        "description": "The ID for a parent category (default: 0 - root category)",
        "default": 0,
        "minimum": 0
      },
      "realtime_start": {
        "type": "string",
        "description": "Start date for real-time period (YYYY-MM-DD format)",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      },
      "realtime_end": {
        "type": "string",
        "description": "End date for real-time period (YYYY-MM-DD format)",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      }
    }
  }
}
```

### Return Value Structure

**Type**: String (JSON-formatted)

**Success Format**:
```typescript
{
  tool: "get_category_children",
  data: Array<{
    id: number,
    name: string,
    parent_id: number,
    notes?: string
  }>,
  metadata: {
    fetch_date: string,       // ISO 8601 timestamp
    parent_category_id: number,
    total_count: number,
    returned_count: number,
    realtime_start: string,   // YYYY-MM-DD
    realtime_end: string      // YYYY-MM-DD
  }
}
```

**Error Format**:
```typescript
{
  tool: "get_category_children",
  error: string,
  category_id?: number
}
```

### Related FRED API Endpoint

**Official Documentation**: https://fred.stlouisfed.org/docs/api/fred/category_children.html

**Base URL**: `https://api.stlouisfed.org/fred/category/children`

**Required Parameters**: `api_key`, `file_type=json`

**Optional Parameters**: `category_id`, `realtime_start`, `realtime_end`

---

## Conclusion

The `get_category_children` tool is essential for navigating FRED's hierarchical category taxonomy. Combined with `get_category`, it enables complete top-down and bottom-up exploration of economic data organization.

**Key Takeaways**:
- Start from root (category_id=0) for top-level exploration
- Empty data array indicates leaf category (contains series)
- Cache results - category structures rarely change
- Use depth limits to prevent excessive recursion
- Combine with other tools for complete data workflows

**Typical Workflow**:
1. Get top-level categories: `get_category_children(0)`
2. Drill into topic: `get_category_children(specific_id)`
3. Repeat until finding leaf category
4. Search for series in leaf category
5. Retrieve series data with `get_series_observations`

For additional assistance:
- See `FRED_CATEGORY_REFERENCE.MD` for parent category info
- See `FRED_OBSERVATIONS_REFERENCE.MD` for retrieving series data
- Visit https://fred.stlouisfed.org for official FRED documentation
