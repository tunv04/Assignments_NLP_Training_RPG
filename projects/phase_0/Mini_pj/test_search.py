from app.db.session import SessionLocal
from app.repositories.product_repository import ProductRepository
from app.services.search_service import SearchService

db = SessionLocal()
repo = ProductRepository(db)
search_service = SearchService(repo)

# Test search
queries = ['gan', 'vitmin', 'bo gan']
for q in queries:
    results = search_service.search(q, limit=3)
    print(f'\nTìm kiếm: "{q}" -> {len(results)} kết quả')
    for r in results[:2]:
        print(f'  [{r["match_type"]}] {r["name"][:50]}... (score: {r["score"]})')

db.close()
