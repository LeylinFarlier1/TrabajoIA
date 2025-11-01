"""
Quick test script for get_series_tags tool.
"""
import sys
import json
import time

# Add src to path
sys.path.insert(0, 'src')

from trabajo_ia_server.tools.fred.get_series_tags import get_series_tags

print('=== Testing get_series_tags ===\n')

# Test 1: STLFSI
print('Test 1: Get tags for STLFSI (St. Louis Financial Stress Index)')
start = time.time()
try:
    result = get_series_tags('STLFSI')
    elapsed = time.time() - start
    data = json.loads(result)

    if 'error' in data:
        print(f'  ERROR: {data["error"]}')
    else:
        print(f'  Time: {elapsed:.2f}s')
        print(f'  Series ID: {data["metadata"]["series_id"]}')
        print(f'  Total tags: {data["metadata"]["returned_count"]}')
        if data['data']:
            print(f'  Sample tags: {[tag["name"] for tag in data["data"][:5]]}')
            print(f'  Tag groups: {list(set(tag["group_id"] for tag in data["data"]))}')
except Exception as e:
    print(f'  ERROR: {str(e)}')
    import traceback
    traceback.print_exc()
print()

# Test 2: GDP
print('Test 2: Get tags for GDP')
start = time.time()
try:
    result = get_series_tags('GDP')
    elapsed = time.time() - start
    data = json.loads(result)

    if 'error' in data:
        print(f'  ERROR: {data["error"]}')
    else:
        print(f'  Time: {elapsed:.2f}s')
        print(f'  Total tags: {data["metadata"]["returned_count"]}')
        print(f'  Tags: {[tag["name"] for tag in data["data"]]}')
except Exception as e:
    print(f'  ERROR: {str(e)}')
print()

# Test 3: UNRATE with sorting
print('Test 3: Get tags for UNRATE sorted by popularity')
start = time.time()
try:
    result = get_series_tags('UNRATE', order_by='popularity', sort_order='desc')
    elapsed = time.time() - start
    data = json.loads(result)

    if 'error' in data:
        print(f'  ERROR: {data["error"]}')
    else:
        print(f'  Time: {elapsed:.2f}s')
        print(f'  Total tags: {data["metadata"]["returned_count"]}')
        print(f'  Top 3 tags by popularity:')
        for i, tag in enumerate(data['data'][:3], 1):
            print(f'    {i}. {tag["name"]} (popularity: {tag["popularity"]}, group: {tag["group_id"]})')
except Exception as e:
    print(f'  ERROR: {str(e)}')
print()

# Test 4: Invalid series ID (error case)
print('Test 4: Invalid series ID (should error gracefully)')
start = time.time()
try:
    result = get_series_tags('INVALID_SERIES_ID_12345')
    elapsed = time.time() - start
    data = json.loads(result)

    if 'error' in data:
        print(f'  Expected error: {data["error"]}')
        print(f'  Time: {elapsed:.2f}s')
    else:
        print(f'  Unexpected success')
except Exception as e:
    print(f'  ERROR: {str(e)}')
print()

print('All tests completed!')
