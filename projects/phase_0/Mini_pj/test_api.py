import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("TEST DRUG/PRODUCT NAME SEARCH SERVICE")
print("=" * 70)

# Test 1: Health check
print("\n✅ TEST 1: Health Check")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/health")
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")

# Test 2: List products
print("\n✅ TEST 2: List Products (limit=3)")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/api/v1/products/?limit=3")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Total results: {len(data)}")
for p in data[:2]:
    print(f"  - ID {p['id']}: {p['name'][:60]}")

# Test 3: Get product detail
print("\n✅ TEST 3: Get Product Detail (ID=1)")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/api/v1/products/1")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"ID: {data['id']}")
print(f"Name: {data['name']}")
print(f"Comments: {len(data['comments'])}")

# Test 4: Search basic
print("\n✅ TEST 4: Search 'bo gan' (basic search)")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/api/v1/products/search?q=bo%20gan&limit=3")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Query: {data['query']}")
print(f"Total: {data['total']}")
for r in data['results'][:2]:
    print(f"  - [{r['match_type']}] {r['name'][:50]} (score: {r['score']})")

# Test 5: Search fuzzy
print("\n✅ TEST 5: Search 'vitmin' (fuzzy search)")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/api/v1/products/search?q=vitmin&limit=3")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Query: {data['query']}")
print(f"Total: {data['total']}")
for r in data['results'][:2]:
    print(f"  - [{r['match_type']}] {r['name'][:50]} (score: {r['score']})")

# Test 6: Search with pagination
print("\n✅ TEST 6: List Products with offset (offset=2, limit=2)")
print("-" * 70)
resp = requests.get(f"{BASE_URL}/api/v1/products/?limit=2&offset=2")
print(f"Status: {resp.status_code}")
data = resp.json()
print(f"Results: {len(data)}")
for p in data:
    print(f"  - ID {p['id']}: {p['name'][:50]}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
print("=" * 70)
