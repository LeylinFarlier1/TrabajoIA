# FRED Category Related Tool – API Reference
## Tool: get_fred_category_related

**Endpoint:** `https://api.stlouisfed.org/fred/category/related`

**Description:** Get related categories for a specific FRED category. Discovers cross-references and semantic links between different parts of FRED's category taxonomy.

---

## Table of Contents

1. [Overview](#overview)
2. [Parameters](#parameters)
3. [Response Format](#response-format)
4. [Usage Examples](#usage-examples)
5. [Use Cases](#use-cases)
6. [Understanding Related Categories](#understanding-related-categories)
7. [Common Examples](#common-examples)
8. [Error Handling](#error-handling)
9. [Performance](#performance)
10. [Best Practices](#best-practices)
11. [Related Tools](#related-tools)

---

## Overview

The `get_fred_category_related` tool retrieves related categories for a specific FRED category. A related category is a one-way relation between 2 categories that is **not part of a parent-child category hierarchy**. Most categories do not have related categories, but when they exist, they provide valuable semantic connections between different organizational hierarchies.

### Key Features

- **Cross-Hierarchy Links**: Connect categories across different organizational structures
- **Semantic Relationships**: Discover thematic connections beyond parent-child
- **Regional Mappings**: Link regional data across different taxonomies
- **Fast Queries**: Typical response time < 0.5s
- **Compact JSON**: AI-optimized format
- **Empty Results**: Returns empty array if no related categories exist

### Why Use Related Categories?

Related categories provide:
- **Navigation Shortcuts**: Jump between different parts of the taxonomy
- **Contextual Links**: Find similar categories organized differently
- **Regional Connections**: Link states/regions across hierarchies
- **Data Discovery**: Uncover alternative paths to relevant data
- **Semantic Understanding**: See how FRED cross-references its own data

---

## Parameters

### Required Parameters

#### `category_id` (integer, REQUIRED)

The ID for a FRED category.

**Format:** Non-negative integer

**Examples:**
```python
32073      # St. Louis Fed District > States in District (has 7 related categories)
125        # Trade Balance (typically no related categories)
32991      # Money, Banking, & Finance
```

**Important Notes:**
- Must be a valid FRED category ID
- Most categories have **no** related categories (returns empty list)
- Related categories are manually curated by FRED
- Relationships are one-way (A→B does not imply B→A)

---

### Optional Parameters

#### `realtime_start` (string, optional)

Start date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

**Examples:**
```python
"2024-01-01"
"2023-06-15"
"2025-11-01"
```

**Use Cases:**
- Historical data analysis
- Time-series consistency
- Vintage data retrieval

---

#### `realtime_end` (string, optional)

End date for the real-time period.

**Format:** YYYY-MM-DD

**Default:** Today's date

**Examples:**
```python
"2024-12-31"
"2023-12-31"
"2025-11-01"
```

**Important Notes:**
- Must be >= realtime_start
- Used with realtime_start for historical periods
- For most use cases, default (today) is sufficient

---

## Response Format

### Success Response

```json
{
  "tool": "get_category_related",
  "data": [
    {
      "id": 149,
      "name": "Arkansas",
      "parent_id": 27281
    },
    {
      "id": 150,
      "name": "Illinois",
      "parent_id": 27281
    },
    {
      "id": 151,
      "name": "Indiana",
      "parent_id": 27281
    }
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 32073,
    "count": 7,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

### Response Fields

#### `data` (array)

Array of related category objects. **Empty array** if no related categories exist.

Each category object contains:
- **id** (integer): Category ID
- **name** (string): Category name
- **parent_id** (integer): Parent category ID in the target hierarchy

#### `metadata` (object)

Query metadata:
- **fetch_date** (string): UTC timestamp when data was retrieved
- **category_id** (integer): The input category ID
- **count** (integer): Number of related categories found
- **realtime_start** (string): Real-time period start date
- **realtime_end** (string): Real-time period end date

---

### Empty Result Response

When a category has no related categories:

```json
{
  "tool": "get_category_related",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 0,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

---

### Error Response

```json
{
  "tool": "get_category_related",
  "error": "Category not found: 999999",
  "category_id": 999999
}
```

---

## Usage Examples

### Example 1: Get Related Categories for St. Louis Fed District

**Request:**
```python
get_fred_category_related(category_id=32073)
```

**Response:**
```json
{
  "tool": "get_category_related",
  "data": [
    {"id": 149, "name": "Arkansas", "parent_id": 27281},
    {"id": 150, "name": "Illinois", "parent_id": 27281},
    {"id": 151, "name": "Indiana", "parent_id": 27281},
    {"id": 152, "name": "Kentucky", "parent_id": 27281},
    {"id": 153, "name": "Mississippi", "parent_id": 27281},
    {"id": 154, "name": "Missouri", "parent_id": 27281},
    {"id": 193, "name": "Tennessee", "parent_id": 27281}
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 32073,
    "count": 7,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Category 32073 is "States in District" under the St. Louis Federal Reserve District hierarchy. It has related categories linking to each state's category in the "Regional Data > States" hierarchy.

---

### Example 2: Category with No Related Categories

**Request:**
```python
get_fred_category_related(category_id=125)
```

**Response:**
```json
{
  "tool": "get_category_related",
  "data": [],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 125,
    "count": 0,
    "realtime_start": "2025-11-01",
    "realtime_end": "2025-11-01"
  }
}
```

**Explanation:**
Most categories, like Trade Balance (125), do not have related categories. This is normal and expected.

---

### Example 3: With Real-Time Period

**Request:**
```python
get_fred_category_related(
    category_id=32073,
    realtime_start="2024-01-01",
    realtime_end="2024-12-31"
)
```

**Response:**
```json
{
  "tool": "get_category_related",
  "data": [
    {"id": 149, "name": "Arkansas", "parent_id": 27281},
    ...
  ],
  "metadata": {
    "fetch_date": "2025-11-01T12:00:00Z",
    "category_id": 32073,
    "count": 7,
    "realtime_start": "2024-01-01",
    "realtime_end": "2024-12-31"
  }
}
```

---

## Use Cases

### 1. Regional Data Navigation

**Scenario:** Exploring state-level data across different organizational hierarchies.

**Example:**
```python
# Get states related to St. Louis Fed District
result = get_fred_category_related(32073)
# Returns Arkansas, Illinois, Indiana, Kentucky, Mississippi, Missouri, Tennessee

# Each state has its own category in Regional Data > States hierarchy
# This allows navigation from Fed District → State categories
```

**Benefits:**
- Jump between Federal Reserve District and State hierarchies
- Find all states in a Fed District
- Access state-specific data from district view

---

### 2. Cross-Reference Discovery

**Scenario:** Finding alternative organizational paths to related data.

**Example:**
```python
# Check if a category has alternative views
result = get_fred_category_related(category_id)

if result["metadata"]["count"] > 0:
    print("Alternative categories found:")
    for cat in result["data"]:
        print(f"  - {cat['name']} (id={cat['id']})")
else:
    print("No alternative category views")
```

---

### 3. Taxonomy Exploration

**Scenario:** Understanding how FRED organizes and cross-references data.

**Example:**
```python
# Explore related categories for context
category_info = get_fred_category(32073)
related = get_fred_category_related(32073)

print(f"Category: {category_info['data']['name']}")
print(f"Related categories: {related['metadata']['count']}")
for cat in related['data']:
    print(f"  → {cat['name']}")
```

---

## Understanding Related Categories

### What Are Related Categories?

Related categories are **one-way semantic links** between categories that exist **outside** the parent-child hierarchy. They represent conceptual relationships manually curated by FRED.

### Key Characteristics

1. **Non-Hierarchical**: Not part of parent-child tree
2. **One-Way**: A→B does not imply B→A
3. **Manually Curated**: Created by FRED staff, not algorithmic
4. **Sparse**: Most categories have zero related categories
5. **Regional Focus**: Often used for geographic cross-references

### Example Relationship

**Category A:** St. Louis Fed District > States in District (32073)
- Parent hierarchy: Federal Reserve Districts

**Related Category B:** Regional Data > States > Missouri (154)
- Parent hierarchy: States

**Relationship:** Links the same state across two different organizational hierarchies.

---

## Common Examples

### Federal Reserve Districts → States

Many Federal Reserve District categories link to state categories:

| District Category | Related State Categories |
|------------------|-------------------------|
| St. Louis District States (32073) | Arkansas, Illinois, Indiana, Kentucky, Mississippi, Missouri, Tennessee |
| Kansas City District States | Colorado, Kansas, Missouri, Nebraska, New Mexico, Oklahoma, Wyoming |
| Atlanta District States | Alabama, Florida, Georgia, Louisiana, Mississippi, Tennessee |

---

## Error Handling

### Common Errors

#### 1. Invalid Category ID

**Error:**
```json
{
  "tool": "get_category_related",
  "error": "Invalid category_id: -1",
  "category_id": -1
}
```

**Cause:** Negative or invalid category_id

**Solution:** Use non-negative integer category IDs

---

#### 2. Category Not Found

**Error:**
```json
{
  "tool": "get_category_related",
  "error": "Category not found: 999999",
  "category_id": 999999
}
```

**Cause:** Category ID does not exist in FRED

**Solution:** Verify category ID using get_fred_category

---

#### 3. Rate Limit Exceeded

**Error:**
```json
{
  "tool": "get_category_related",
  "error": "Rate limit exceeded. Please try again later.",
  "category_id": 32073
}
```

**Cause:** Too many requests to FRED API

**Solution:** Wait and retry. Tool has built-in exponential backoff (3 retries)

---

## Performance

### Response Times

| Scenario | Typical Time | Max Time |
|----------|-------------|----------|
| Categories with related items | 200-500ms | 1s |
| Categories without related items | 150-400ms | 1s |
| First request (cold) | 300-600ms | 1.5s |
| Subsequent requests (warm) | 150-400ms | 1s |

### Performance Characteristics

- **Fast Empty Results**: Queries for categories with no related categories return quickly
- **No Pagination**: All related categories returned in single request
- **Retry Logic**: 3 attempts with exponential backoff (1-5s)
- **Compact JSON**: AI-optimized format minimizes token usage
- **Session Reuse**: HTTP connection pooling for efficiency

---

## Best Practices

### 1. Expect Empty Results

```python
# Most categories have no related categories
result = get_fred_category_related(category_id)

if result["metadata"]["count"] == 0:
    # This is normal and expected
    print("No related categories (this is common)")
else:
    # Process related categories
    for cat in result["data"]:
        print(f"Related: {cat['name']}")
```

---

### 2. Use for Regional Navigation

```python
# Best use case: Regional data exploration
fed_district_states = get_fred_category_related(32073)

# Navigate to each related state category
for state in fed_district_states["data"]:
    state_data = get_fred_category(state["id"])
    print(f"State: {state_data['data']['name']}")
```

---

### 3. Combine with Other Category Tools

```python
# Get category info
category = get_fred_category(32073)
print(f"Category: {category['data']['name']}")

# Get children (hierarchical)
children = get_fred_category_children(32073)
print(f"Children: {children['metadata']['count']}")

# Get related (cross-reference)
related = get_fred_category_related(32073)
print(f"Related: {related['metadata']['count']}")
```

---

### 4. Handle Errors Gracefully

```python
result = get_fred_category_related(category_id)

if "error" in result:
    print(f"Error: {result['error']}")
    # Handle error appropriately
else:
    # Process successful result
    count = result["metadata"]["count"]
    print(f"Found {count} related categories")
```

---

## Related Tools

### Complementary Category Tools

| Tool | Purpose | When to Use |
|------|---------|------------|
| `get_fred_category` | Get category metadata | Get name, parent, notes for a category |
| `get_fred_category_children` | Get child categories | Navigate down the hierarchy |
| `get_fred_category_related` | Get related categories | Find cross-references (this tool) |

### Typical Workflow

```python
# 1. Start with category info
category = get_fred_category(32073)
print(f"Category: {category['data']['name']}")
print(f"Parent ID: {category['data']['parent_id']}")

# 2. Explore children (down the hierarchy)
children = get_fred_category_children(32073)
print(f"Child categories: {children['metadata']['count']}")

# 3. Explore related (cross-references)
related = get_fred_category_related(32073)
print(f"Related categories: {related['metadata']['count']}")

# 4. Navigate to related categories
for cat in related["data"]:
    cat_info = get_fred_category(cat["id"])
    print(f"  → {cat_info['data']['name']}")
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-01 | Initial implementation |

---

## Additional Resources

- **FRED API Documentation**: https://fred.stlouisfed.org/docs/api/fred/
- **FRED Category Endpoint**: https://fred.stlouisfed.org/docs/api/fred/category_related.html
- **FRED Website**: https://fred.stlouisfed.org/
- **Category Browser**: https://fred.stlouisfed.org/categories

---

## Support

For issues or questions:
1. Check FRED API status: https://fred.stlouisfed.org/docs/api/api_status.html
2. Review error messages in response JSON
3. Verify category_id exists using get_fred_category
4. Check API key configuration
5. Review server logs for detailed error information

---

**Last Updated:** 2025-11-01  
**Tool Version:** 1.0.0  
**FRED API Version:** Stable (no versioning)
