# Drug/Product Name Search Service

Backend FastAPI dùng PostgreSQL để lưu dữ liệu sản phẩm/câu bình luận crawl từ
Chiaki.vn và cung cấp API liệt kê, xem chi tiết, tìm kiếm theo tên, mô tả và
comment.

Tài liệu này là hướng dẫn chính cho cách chạy bằng Docker + PostgreSQL. File
`QUICK_START.py` trong repo vẫn là script hướng dẫn cũ cho luồng local/SQLite,
không phải luồng Docker/PostgreSQL hiện tại.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy ORM
- PostgreSQL qua `psycopg2-binary`
- Pydantic/Pydantic Settings
- `rank-bm25` cho BM25 ranking
- `rapidfuzz` cho fuzzy search

## Cấu trúc chính

```text
Mini_pj/
├── app/
│   ├── main.py                    # Khởi tạo FastAPI app và /health
│   ├── core/config.py             # Đọc settings từ env và .env
│   ├── db/session.py              # SQLAlchemy engine/session/get_db
│   ├── db/base.py                 # Import model để create_all thấy metadata
│   ├── models/product.py          # Product và Comment ORM models
│   ├── schemas/product.py         # Pydantic response schemas
│   ├── repositories/
│   │   └── product_repository.py  # Query/list/detail/search_basic/upsert
│   ├── services/
│   │   ├── text_normalizer.py     # Chuẩn hóa tiếng Việt cho search
│   │   └── search_service.py      # BM25 + basic + fuzzy search
│   └── api/v1/
│       ├── router.py              # Include product routes
│       └── product_routes.py      # API /api/v1/products
├── scripts/
│   ├── create_tables.py           # Tạo schema trong DB
│   └── import_products.py         # Import JSON/JSONL vào DB
├── data/
│   └── chiaki_products.json       # File dữ liệu được mount vào Docker
├── craw.py                        # Script crawl dữ liệu từ Chiaki.vn
├── test_api.py                    # Test API qua HTTP, cần server đang chạy
├── test_search.py                 # Test SearchService trực tiếp
├── Dockerfile                     # Image backend, chạy Uvicorn port 8001
├── docker-compose.yml             # PostgreSQL + backend
├── .env.docker.example            # Biến PostgreSQL mẫu
└── requirements.txt
```

## Chạy Bằng Docker Và PostgreSQL

Yêu cầu: Docker Desktop đang chạy.

Từ PowerShell:

```powershell
cd d:\TRAINING_NLP_RPG\Mini_pj
```

Compose đã có giá trị mặc định:

```text
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=medicine_search
POSTGRES_PORT=5433
```

Nếu muốn đổi user/password/database/host port, thêm các biến trên vào file
`.env` trong thư mục `Mini_pj`, hoặc set trực tiếp trong PowerShell trước khi
`docker compose up`.

Build image backend:

```powershell
$env:DOCKER_BUILDKIT="0"
docker build -t mini_pj-backend:latest .
```

Lý do dùng `DOCKER_BUILDKIT=0`: trên máy hiện tại, `docker compose build` qua
buildx có thể bị treo. Nếu Docker Desktop của bạn buildx ổn, có thể dùng:

```powershell
docker compose build
```

Chạy PostgreSQL và backend:

```powershell
docker compose up -d --no-build
```

Tạo bảng và import dữ liệu:

```powershell
docker compose run --rm backend python -m scripts.create_tables
docker compose run --rm backend python -m scripts.import_products
```

Kiểm tra service:

```powershell
curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/products/?limit=5"
curl "http://localhost:8000/api/v1/products/search?q=bo%20gan&limit=5"
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Port Và Kết Nối Database

Trong Docker:

- Backend container chạy Uvicorn ở port `8001`.
- Máy host gọi backend qua `http://localhost:8000`.
- Compose map `8000:8001`.
- PostgreSQL container chạy port nội bộ `5432`.
- Máy host kết nối PostgreSQL qua port mặc định `5433`.

`DATABASE_URL` trong backend container được compose override thành:

```text
postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@postgres:5432/<POSTGRES_DB>
```

Trong Docker, backend phải kết nối tới hostname service `postgres`. Không dùng
`localhost` trong `DATABASE_URL` của container backend, vì `localhost` lúc đó là
chính container backend, không phải container PostgreSQL.

Kết nối PostgreSQL từ máy host bằng `psql`:

```powershell
psql -h localhost -p 5433 -U postgres -d medicine_search
```

## Lệnh Quản Lý Docker

Xem trạng thái:

```powershell
docker compose ps
```

Xem log backend:

```powershell
docker compose logs -f backend
```

Xem log PostgreSQL:

```powershell
docker compose logs -f postgres
```

Dừng container nhưng giữ data PostgreSQL:

```powershell
docker compose down
```

Reset toàn bộ data PostgreSQL trong Docker volume:

```powershell
docker compose down -v
docker compose up -d --no-build
docker compose run --rm backend python -m scripts.create_tables
docker compose run --rm backend python -m scripts.import_products
```

## Dữ Liệu Import

Trong Docker, thư mục `./data` trên máy host được mount read-only vào `/app/data`
trong backend container. Vì Dockerfile chỉ copy `app/` và `scripts/`, file dữ
liệu cần nằm ở:

```text
Mini_pj/data/chiaki_products.json
```

Script `scripts.import_products` hỗ trợ:

- JSON array: `[{"name": "...", ...}, ...]`
- Một JSON object đơn lẻ
- JSONL: mỗi dòng là một JSON object

Các key được nhận diện:

```text
name:        name, title, product_name
url:         url, link, product_url
description: description, desc, detail, content, summary
category:    category, category_name, cate, breadcrumb
price:       price, sale_price, current_price, price_text
source:      source, site, domain
comments:    comments, reviews, feedbacks, review
```

Với comment, script đọc các field:

```text
author, rating, content/comment/text/review/body/message, date
```

Import dùng cơ chế upsert theo `url`:

- Nếu URL chưa có trong DB: tạo product mới.
- Nếu URL đã có: update thông tin product, xóa comment cũ của product đó và
  ghi lại comment mới từ file JSON.
- Nếu record không có `name`: bỏ qua và tăng `Skipped`.

## Database Schema

`products`:

```text
id                     INTEGER PRIMARY KEY
name                   VARCHAR NOT NULL
normalized_name        VARCHAR NOT NULL, index=True
url                    VARCHAR UNIQUE, index=True
description            TEXT
normalized_description TEXT
category               VARCHAR
price                  VARCHAR
source                 VARCHAR, default="chiaki.vn"
created_at             DATETIME, default=datetime.utcnow
```

`comments`:

```text
id                 INTEGER PRIMARY KEY
product_id         INTEGER NOT NULL, FK products.id ON DELETE CASCADE, index=True
author             VARCHAR NULL
rating             INTEGER NULL
content            TEXT NOT NULL
normalized_content TEXT NOT NULL
date               VARCHAR NULL
```

Quan hệ:

- `Product.comments`: one-to-many tới `Comment`
- Cascade: xóa product sẽ xóa comment liên quan

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "drug-product-name-search-service"
}
```

### List Products

```http
GET /api/v1/products/?limit=20&offset=0
```

Query parameters:

- `limit`: integer, từ `1` đến `100`, mặc định `20`
- `offset`: integer, từ `0`, mặc định `0`

Response là list product, không kèm comments.

### Product Detail

```http
GET /api/v1/products/{product_id}
```

Response trả product kèm toàn bộ comments của product đó. Nếu không tìm thấy:

```json
{
  "detail": "Product not found"
}
```

### Search Products

```http
GET /api/v1/products/search?q=bo%20gan&limit=10
```

Query parameters:

- `q`: string bắt buộc, tối thiểu 2 ký tự
- `limit`: integer, từ `1` đến `50`, mặc định `10`

Response:

```json
{
  "query": "bo gan",
  "total": 2,
  "results": [
    {
      "id": 1,
      "name": "...",
      "url": "...",
      "description": "...",
      "category": "...",
      "price": "...",
      "source": "chiaki.vn",
      "comments_count": 10,
      "comments": [
        {
          "id": 1,
          "author": "...",
          "rating": 5,
          "content": "...",
          "date": "13:53, 05/04/2026"
        }
      ],
      "score": 100.0,
      "match_type": "basic"
    }
  ]
}
```

Trong kết quả search, `comments` chỉ lấy tối đa 3 comment đầu tiên để response
không quá lớn. `comments_count` vẫn là tổng số comment của product.

`match_type` có thể là:

- `bm25`: kết quả đến từ BM25 ranking
- `basic`: kết quả exact/substring match tốt nhất
- `fuzzy`: kết quả fuzzy fallback tốt nhất

Nếu một product match nhiều stage, service giữ score cao nhất và `match_type`
ứng với stage tạo ra score đó.

## Search Hoạt Động Như Thế Nào

Search nằm trong `app/services/search_service.py` và dùng dữ liệu đã chuẩn hóa
từ `TextNormalizer`.

### 1. Chuẩn Hóa Text

`TextNormalizer.normalize()` xử lý cả query và dữ liệu import:

1. Chuyển `Đ/đ` thành `D/d`.
2. Bỏ dấu tiếng Việt bằng Unicode normalization.
3. Lowercase.
4. Chỉ giữ chữ cái `a-z`, số `0-9` và khoảng trắng.
5. Chuẩn hóa nhiều khoảng trắng thành một khoảng trắng.
6. Loại stop words phổ biến như `thuoc`, `vien`, `uong`, `cho`, `cua`, `va`,
   `tot`, `hieu`, `qua`.

Ví dụ:

```text
"Viên uống Bổ Gan!!!" -> "bo gan"
"Vitamin Đ"           -> "vitamin d"
"SẢN PHẨM tốt quá"    -> "san pham"
```

Khi import, script lưu thêm:

- `products.normalized_name`
- `products.normalized_description`
- `comments.normalized_content`

Nhờ vậy search không phụ thuộc người dùng gõ có dấu hay không dấu.

### 2. Dựng BM25 Corpus

Khi `SearchService` được khởi tạo, service gọi:

```python
product_repository.list_all_with_comments()
```

Sau đó tạo corpus cho BM25 bằng cách ghép:

```text
normalized_name + normalized_description + normalized_content của các comments
```

Corpus được tách token bằng `.split()` rồi đưa vào `BM25Okapi`.

Lưu ý hiệu năng: route hiện tại tạo `SearchService` mới cho mỗi request search,
nên BM25 index cũng được dựng lại trong request đó. Với dữ liệu khoảng vài trăm
sản phẩm vẫn chạy được, nhưng nếu dữ liệu lớn hơn thì nên cache service/index ở
scope ứng dụng.

### 3. Stage 1: BM25 Ranking

Query sau khi normalize được tách thành tokens. BM25 tính điểm giữa query tokens
và corpus từng product.

Code hiện tại:

- Bỏ qua product có `bm25_score < 0.8`.
- Score cuối stage BM25:

```text
bm25_score * intent_boost * 0.9
```

Kết quả stage này có `match_type="bm25"`.

BM25 phù hợp khi query có nhiều từ và cần xếp hạng theo mức độ liên quan tổng
thể trong tên, mô tả và comment.

### 4. Stage 2: Basic Search

Repository chạy SQL `LIKE` trên PostgreSQL với pattern:

```text
%<normalized_query>%
```

Các field được tìm:

- `Product.normalized_name`
- `Product.normalized_description`
- `Comment.normalized_content`

Basic score:

```text
100  nếu normalized_query bằng đúng normalized_name
96   nếu normalized_query nằm trong normalized_name
87   nếu normalized_query nằm trong normalized_description
86   nếu category chứa một số từ khóa tiêu hóa hard-coded
80   nếu normalized_query nằm trong normalized_content của comment
67   fallback nếu vào được basic nhưng không trúng rule trên
```

Score cuối stage basic:

```text
basic_score * intent_boost * 1.15
```

Stage basic được nhân `1.15`, nên exact/substring match thường được ưu tiên hơn
BM25 nếu cùng một product có nhiều loại match.

Kết quả stage này có `match_type="basic"`.

### 5. Stage 3: Fuzzy Search

Fuzzy search là fallback cho trường hợp người dùng gõ sai, ví dụ:

```text
"vitmin" -> "vitamin"
```

Service dùng `rapidfuzz` và lấy điểm cao nhất trong ba thuật toán:

- `fuzz.WRatio`
- `fuzz.partial_ratio`
- `fuzz.token_set_ratio`

Các field và trọng số:

```text
normalized_name        * 1.00
normalized_description * 0.83
normalized_content     * 0.79
```

Nếu fuzzy score thấp hơn `fuzzy_threshold=76.0`, product bị bỏ qua.

Score cuối stage fuzzy:

```text
fuzzy_score * intent_boost * 0.85
```

Nếu product đã có score trên `80` từ stage trước, fuzzy stage bỏ qua product đó
để giảm tính toán.

Kết quả stage này có `match_type="fuzzy"`.

### 6. Intent Boost

`_intent_boost()` tăng score khi query và product thể hiện cùng ý định tìm kiếm.
Boost tối đa bị giới hạn ở `3.3`.

Các nhóm synonym hiện có:

```text
dau bung
tieu hoa
men vi sinh
giam can
tang chieu cao
tang suc de khang
vitamin
omega
magie
canxi
```

Các rule chính:

- Nếu query chứa synonym và product name/description/category cũng chứa synonym
  cùng nhóm: cộng `1.3`.
- Nếu product chứa strong health intent như `dau bung`, `tieu hoa`, `men vi
  sinh`, `giam can`, `tang chieu cao`: cộng `1.25`.
- Nếu query gốc có chữ `thuoc` và category liên quan `tieu hoa`, `nhuan trang`,
  `vitamin`, `canxi`: cộng `0.95`.
- Mỗi từ query dài từ 3 ký tự xuất hiện trong name hoặc description: cộng `0.45`.

### 7. Gộp Và Sắp Xếp Kết Quả

Kết quả từ ba stage được gộp theo `product.id`.

- Nếu product chưa có trong `hits`: thêm mới.
- Nếu product đã có: chỉ thay nếu score mới cao hơn score hiện tại.

Cuối cùng sort theo:

```text
score giảm dần
name tăng dần theo alphabet nếu cùng score
```

Sau đó trả về tối đa `limit` kết quả.

## Chạy Local Không Docker

Luồng khuyến nghị vẫn là Docker. Nếu muốn chạy backend trực tiếp trên máy host
nhưng dùng PostgreSQL, cần có PostgreSQL đang chạy và database đã tồn tại.

Ví dụ dùng PostgreSQL container của compose nhưng chạy backend local:

```powershell
cd d:\TRAINING_NLP_RPG\Mini_pj
docker compose up -d postgres
```

File `.env` trên host:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/medicine_search
```

Sau đó:

```powershell
pip install -r requirements.txt
python -m scripts.create_tables
python -m scripts.import_products
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Test

Với Docker stack đang chạy:

```powershell
python test_api.py
```

`test_api.py` dùng package `requests`. Nếu môi trường Python local chưa có:

```powershell
pip install requests
```

Test trực tiếp service layer:

```powershell
python test_search.py
```

`test_search.py` dùng `DATABASE_URL` từ `.env`/environment của máy host, không
tự dùng biến môi trường trong Docker container.

## Crawler

`craw.py` crawl sản phẩm từ:

```text
https://chiaki.vn/thuc-pham-chuc-nang
```

Script này dùng `requests` và `beautifulsoup4`, nhưng hai package đó không nằm
trong `requirements.txt` backend. Nếu muốn chạy crawler:

```powershell
pip install requests beautifulsoup4
python craw.py
```

Output mặc định:

```text
chiaki_products.json
```

Để Docker import được, đặt/copy file dữ liệu vào:

```text
data/chiaki_products.json
```

## Troubleshooting

### Docker build bị treo

Dùng legacy builder:

```powershell
$env:DOCKER_BUILDKIT="0"
docker build -t mini_pj-backend:latest .
```

### Backend báo `ModuleNotFoundError: No module named 'rank_bm25'`

Image đang dùng requirements cũ. Build lại image và recreate backend:

```powershell
$env:DOCKER_BUILDKIT="0"
docker build -t mini_pj-backend:latest .
docker compose up -d --no-build --force-recreate backend
```

### Không kết nối được PostgreSQL trong Docker

Kiểm tra container:

```powershell
docker compose ps
docker compose logs postgres
```

Trong backend container, `DATABASE_URL` phải dùng host `postgres`, không phải
`localhost`.

### `No such table: products`

Chưa tạo bảng:

```powershell
docker compose run --rm backend python -m scripts.create_tables
```

### Search không có dữ liệu

Chưa import hoặc import nhầm file:

```powershell
docker compose run --rm backend python -m scripts.import_products
```

Trong Docker, kiểm tra file này tồn tại:

```text
Mini_pj/data/chiaki_products.json
```

### Port bị trùng

Backend host port nằm ở `docker-compose.yml`:

```yaml
ports:
  - "8000:8001"
```

Đổi `8000` thành port khác, ví dụ:

```yaml
ports:
  - "8002:8001"
```

PostgreSQL host port được điều khiển bằng `POSTGRES_PORT`, mặc định là `5433`.

### Reset sạch PostgreSQL

Lệnh này xóa volume database:

```powershell
docker compose down -v
docker compose up -d --no-build
docker compose run --rm backend python -m scripts.create_tables
docker compose run --rm backend python -m scripts.import_products
```
