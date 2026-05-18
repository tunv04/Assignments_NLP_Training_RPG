#!/usr/bin/env python3
"""
Quick Start Guide for Drug/Product Name Search Service
Chạy script này để xem tất cả lệnh cần thiết
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════════════════════╗
║              DRUG/PRODUCT NAME SEARCH SERVICE - QUICK START                ║
╚════════════════════════════════════════════════════════════════════════════╝

📁 WORKING DIRECTORY:
  d:\\TRAINING_NLP_RPG\\Mini_pj

⚡ QUICK COMMANDS:

1️⃣  INSTALL DEPENDENCIES
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $ pip install -r requirements.txt
  
  ✅ Installs: fastapi, uvicorn, sqlalchemy, pydantic, rapidfuzz, python-dotenv

2️⃣  CREATE DATABASE TABLES
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $ python -m scripts.create_tables
  
  ✅ Creates: data/medicine_search.db with products + comments tables

3️⃣  IMPORT DATA FROM JSON
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $ python -m scripts.import_products
  
  ✅ Imports: 400+ products from chiaki_products.json
  ✅ Auto-normalizes: Vietnamese text (remove accents)
  ✅ Result: "Inserted: 0, Updated: 400, Skipped: 0"

4️⃣  START API SERVER
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  $ $env:PYTHONPATH="d:\\TRAINING_NLP_RPG\\Mini_pj"
  $ uvicorn app.main:app --host 127.0.0.1 --port 8000
  
  ✅ Server running on: http://127.0.0.1:8000
  ✅ Swagger docs: http://127.0.0.1:8000/docs
  ✅ ReDoc: http://127.0.0.1:8000/redoc

5️⃣  TEST API ENDPOINTS
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Option A: Python Script
    $ python test_api.py
  
  Option B: Manual Curl
    $ curl http://127.0.0.1:8000/health
    $ curl "http://127.0.0.1:8000/api/v1/products/?limit=5"
    $ curl "http://127.0.0.1:8000/api/v1/products/1"
    $ curl "http://127.0.0.1:8000/api/v1/products/search?q=bo%20gan&limit=3"
    $ curl "http://127.0.0.1:8000/api/v1/products/search?q=vitmin&limit=3"

📊 EXPECTED RESULTS:

✅ Health Check:
  {"status": "ok", "service": "drug-product-name-search-service"}

✅ List Products:
  [{"id": 1, "name": "...", "url": "...", ...}, ...]

✅ Product Detail:
  {"id": 1, "name": "...", "comments": [...], ...}

✅ Search "bo gan":
  Results with: "Bổ Gan", "Giảm Cân" (basic match, score: 100)

✅ Search "vitmin":
  Results with: "Vitamin" (fuzzy match, score: ~83)

🔧 KEY FEATURES:

  ✨ Text Normalization
    "Viên Bổ Gan" → "vien bo gan"
    
  🔍 Basic Search
    Exact/substring match in: name, description, comments
    
  🎯 Fuzzy Search
    "vitmin" → finds "vitamin"
    Threshold: 76% similarity
    
  📑 Pagination
    limit (1-100), offset (≥0)
    
  🗄️ Database
    SQLite (data/medicine_search.db)
    400+ products × 2000+ comments

🛠️ TROUBLESHOOTING:

  ❌ "ModuleNotFoundError: No module named 'app'"
     → Run from Mini_pj directory with PYTHONPATH set
     
  ❌ "No such table: products"
     → Run: python -m scripts.create_tables
     
  ❌ Search returns 0 results
     → Run: python -m scripts.import_products
     
  ❌ Port 8000 already in use
     → Use different port: --port 8001

📚 DOCUMENTATION:

  - Full API Docs: README.md
  - Swagger UI: http://127.0.0.1:8000/docs
  - Code Structure: See app/ directory
  - Database: See app/models/product.py

🎯 PROJECT STRUCTURE:

  app/
    ├── main.py                     # FastAPI app
    ├── core/config.py              # Settings
    ├── db/session.py               # SQLAlchemy setup
    ├── models/product.py           # Database models
    ├── schemas/product.py          # Pydantic schemas
    ├── repositories/               # Database layer
    ├── services/                   # Business logic
    └── api/v1/                     # Route handlers
  
  scripts/
    ├── create_tables.py            # Create DB schema
    └── import_products.py          # Import JSON data

✅ STATUS: ALL SYSTEMS GO! 🚀

Next step: Run the 5 quick commands above and enjoy!

"""

if __name__ == "__main__":
    print(QUICK_START)
    
    print("\n📋 SUMMARY:")
    print("=" * 80)
    import os
    from pathlib import Path
    
    mini_pj = Path("d:\\TRAINING_NLP_RPG\\Mini_pj")
    
    # Check files
    files_to_check = {
        "config.py": mini_pj / "app" / "core" / "config.py",
        "session.py": mini_pj / "app" / "db" / "session.py",
        "product.py": mini_pj / "app" / "models" / "product.py",
        "search_service.py": mini_pj / "app" / "services" / "search_service.py",
        "main.py": mini_pj / "app" / "main.py",
        "create_tables.py": mini_pj / "scripts" / "create_tables.py",
        "import_products.py": mini_pj / "scripts" / "import_products.py",
        "requirements.txt": mini_pj / "requirements.txt",
        ".env": mini_pj / ".env",
        "README.md": mini_pj / "README.md",
    }
    
    for name, path in files_to_check.items():
        status = "✅" if path.exists() else "❌"
        print(f"{status} {name}")
    
    print("=" * 80)
