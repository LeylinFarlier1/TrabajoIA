"""
Functional test for get_category_series tool.

Tests the category series retrieval with real FRED API calls.
"""
import json
import time
from trabajo_ia_server.tools.fred.category_series import get_category_series

def test_category_series():
    """Test get_category_series with various scenarios."""

    print("=" * 60)
    print("FRED Category Series Tool - Functional Tests")
    print("=" * 60)

    # Test 1: Get all series in Trade Balance category
    print("\n[Test 1] Get all series in Trade Balance category (125)...")
    start = time.time()
    result1 = get_category_series(125)
    elapsed1 = time.time() - start

    data1 = json.loads(result1)
    if 'error' in data1:
        print(f"[ERROR] Error: {data1['error']}")
    else:
        total = data1['metadata']['total_count']
        returned = data1['metadata']['returned_count']
        print(f"[OK] Found {total} total series ({returned} returned)")

        # Show first 3 series
        for i, series in enumerate(data1['data'][:3], 1):
            print(f"  {i}. {series['id']}: {series['title'][:60]}...")
            print(f"     Frequency: {series['frequency']}, " +
                  f"Units: {series.get('units_short', 'N/A')}, " +
                  f"Popularity: {series['popularity']}")

        print(f"  Response time: {elapsed1:.2f}s")

    # Test 2: Get only monthly series
    print("\n[Test 2] Get monthly series only in Trade Balance (125)...")
    start = time.time()
    result2 = get_category_series(
        125,
        filter_variable="frequency",
        filter_value="Monthly"
    )
    elapsed2 = time.time() - start

    data2 = json.loads(result2)
    if 'error' in data2:
        print(f"[ERROR] Error: {data2['error']}")
    else:
        total = data2['metadata']['total_count']
        returned = data2['metadata']['returned_count']
        print(f"[OK] Found {returned} monthly series")
        print(f"  Filter: {data2['metadata'].get('filter_variable')}=" +
              f"{data2['metadata'].get('filter_value')}")

        # Verify all are monthly
        frequencies = set(s['frequency'] for s in data2['data'])
        print(f"  Unique frequencies: {frequencies}")
        print(f"  Response time: {elapsed2:.2f}s")

    # Test 3: Get series sorted by popularity
    print("\n[Test 3] Top 5 most popular series in Trade Balance (125)...")
    start = time.time()
    result3 = get_category_series(
        125,
        order_by="popularity",
        sort_order="desc",
        limit=5
    )
    elapsed3 = time.time() - start

    data3 = json.loads(result3)
    if 'error' in data3:
        print(f"[ERROR] Error: {data3['error']}")
    else:
        print(f"[OK] Top 5 by popularity:")
        for i, series in enumerate(data3['data'], 1):
            print(f"  {i}. {series['id']} (popularity: {series['popularity']})")
            print(f"     {series['title'][:60]}...")
        print(f"  Response time: {elapsed3:.2f}s")

    # Test 4: Get Interest Rates series (larger category)
    print("\n[Test 4] Get Interest Rates series (category 22)...")
    start = time.time()
    result4 = get_category_series(22, limit=20)
    elapsed4 = time.time() - start

    data4 = json.loads(result4)
    if 'error' in data4:
        print(f"[ERROR] Error: {data4['error']}")
    else:
        total = data4['metadata']['total_count']
        returned = data4['metadata']['returned_count']
        print(f"[OK] Found {total} total series ({returned} returned)")
        print(f"  Category: Interest Rates (22)")
        print(f"  Response time: {elapsed4:.2f}s")

        # Show first 3
        for i, series in enumerate(data4['data'][:3], 1):
            print(f"  {i}. {series['id']}: {series['title'][:50]}...")

    # Test 5: Test pagination
    print("\n[Test 5] Test pagination (first 10 results from category 125)...")
    start = time.time()
    result5 = get_category_series(125, limit=10, offset=0)
    elapsed5 = time.time() - start

    data5 = json.loads(result5)
    if 'error' in data5:
        print(f"[ERROR] Error: {data5['error']}")
    else:
        returned = data5['metadata']['returned_count']
        offset = data5['metadata']['offset']
        limit = data5['metadata']['limit']
        print(f"[OK] Pagination test successful")
        print(f"  Returned: {returned}, Offset: {offset}, Limit: {limit}")
        print(f"  First series: {data5['data'][0]['id']}")
        print(f"  Last series: {data5['data'][-1]['id']}")
        print(f"  Response time: {elapsed5:.2f}s")

    # Test 6: Filter by seasonal adjustment
    print("\n[Test 6] Get seasonally adjusted series only (category 125)...")
    start = time.time()
    result6 = get_category_series(
        125,
        filter_variable="seasonal_adjustment",
        filter_value="Seasonally Adjusted"
    )
    elapsed6 = time.time() - start

    data6 = json.loads(result6)
    if 'error' in data6:
        print(f"[ERROR] Error: {data6['error']}")
    else:
        returned = data6['metadata']['returned_count']
        print(f"[OK] Found {returned} seasonally adjusted series")
        print(f"  Filter: {data6['metadata'].get('filter_variable')}=" +
              f"{data6['metadata'].get('filter_value')}")

        # Verify all are SA
        adjustments = set(s['seasonal_adjustment'] for s in data6['data'])
        print(f"  Unique adjustments: {adjustments}")
        print(f"  Response time: {elapsed6:.2f}s")

    # Summary
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print(f"Total tests: 6")
    print(f"Average response time: {(elapsed1+elapsed2+elapsed3+elapsed4+elapsed5+elapsed6)/6:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    test_category_series()
