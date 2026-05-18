"""
Crawler thu thập thông tin sản phẩm từ chiaki.vn/thuc-pham-chuc-nang
Chỉ dùng requests + BeautifulSoup (không cần Selenium).

Cài đặt:
    pip install requests beautifulsoup4

Chạy:
    python chiaki_crawler.py
"""

import json
import time
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Cấu hình ────────────────────────────────────────────────────────────────
BASE_URL      = "https://chiaki.vn"
CATEGORY_URL  = "https://chiaki.vn/thuc-pham-chuc-nang"
OUTPUT_FILE   = "chiaki_products.json"
DELAY         = 1.0   # giây giữa mỗi request (đừng giảm dưới 1)
MAX_PAGES     = 10   # 1 trang ~ 30 sp. Tăng lên để lấy nhiều hơn.
MAX_PRODUCTS  = None  # None = không giới hạn; đặt số nguyên để giới hạn

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
    "Referer": "https://chiaki.vn/",
}


# ════════════════════════════════════════════════════════════════════════════
#  TIỆN ÍCH
# ════════════════════════════════════════════════════════════════════════════

def get_soup(url: str) -> BeautifulSoup | None:
    """Gửi GET request và trả về BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        log.warning(f"Lỗi request [{url}]: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════
#  BƯỚC 1 – THU THẬP URL SẢN PHẨM TỪ TRANG DANH MỤC
# ════════════════════════════════════════════════════════════════════════════

def parse_products_from_listing(soup: BeautifulSoup) -> list[dict]:
    """
    Phân tích trang danh mục, lấy name, url, price từ mỗi .product-item.

    Cấu trúc HTML chiaki.vn (đã xác nhận qua inspect):
      div.product-item
        h3.product-title > a            ← tên + href
        div.product-price > span + sup  ← giá hiện tại (vd: 375.000đ)
        div.product-price-old           ← giá gốc (nếu đang sale)
    """
    results = []

    for item in soup.select("div.product-item"):
        # Tên & URL
        title_el = item.select_one("h3.product-title a")
        if not title_el:
            continue
        name = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        url  = urljoin(BASE_URL, href) if href else ""

        # Giá hiện tại: lấy tất cả text con trong div.product-price
        price_el = item.select_one("div.product-price")
        price = ""
        if price_el:
            # Gộp span + sup: "375.000" + "đ" → "375.000đ"
            price = "".join(price_el.get_text(separator="", strip=True).split())

        # Giá gốc (nếu có)
        old_el  = item.select_one("div.product-price-old")
        price_old = ""
        if old_el:
            price_old = "".join(old_el.get_text(separator="", strip=True).split())

        results.append({
            "name":      name,
            "url":       url,
            "price":     price,
            "price_old": price_old,
        })

    return results


def collect_product_stubs() -> list[dict]:
    """
    Duyệt nhiều trang danh mục (URL dạng ?page=N).
    Trả về list dict cơ bản: {name, url, price, price_old}.
    """
    all_items: list[dict] = []
    seen_urls: set[str]   = set()

    for page in range(1, MAX_PAGES + 1):
        url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}?page={page}"
        log.info(f"📄 Trang {page}: {url}")

        soup = get_soup(url)
        if not soup:
            log.warning("  → Không lấy được trang, dừng.")
            break

        items = parse_products_from_listing(soup)
        if not items:
            log.info("  → Không còn sản phẩm, dừng phân trang.")
            break

        new_count = 0
        for item in items:
            if item["url"] and item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                all_items.append(item)
                new_count += 1

        log.info(f"  → {new_count} sản phẩm mới (tổng: {len(all_items)})")

        if MAX_PRODUCTS and len(all_items) >= MAX_PRODUCTS:
            all_items = all_items[:MAX_PRODUCTS]
            log.info(f"Đã đủ {MAX_PRODUCTS} sản phẩm.")
            break

        time.sleep(DELAY)

    return all_items


# ════════════════════════════════════════════════════════════════════════════
#  BƯỚC 2 – CRAWL TRANG CHI TIẾT SẢN PHẨM
# ════════════════════════════════════════════════════════════════════════════

# def parse_breadcrumb(soup: BeautifulSoup) -> str:
#     """Lấy breadcrumb, thử nhiều selector và JSON-LD."""
#     # Kiểu 1: ol/ul.breadcrumb li
#     for sel in ("ol.breadcrumb li", "ul.breadcrumb li", ".breadcrumb-item"):
#         items = soup.select(sel)
#         if items:
#             texts = [i.get_text(strip=True) for i in items if i.get_text(strip=True)]
#             if texts and texts[0].lower() in ("trang chủ", "home"):
#                 texts = texts[1:]
#             return " > ".join(texts)

#     # Kiểu 2: JSON-LD BreadcrumbList
#     for script in soup.select("script[type='application/ld+json']"):
#         try:
#             data = json.loads(script.string or "")
#             if data.get("@type") == "BreadcrumbList":
#                 elems = sorted(data.get("itemListElement", []),
#                                key=lambda x: x.get("position", 0))
#                 texts = []
#                 for e in elems:
#                     n = e.get("item", {}).get("name") or e.get("name", "")
#                     if n and n.lower() not in ("trang chủ", "home"):
#                         texts.append(n)
#                 return " > ".join(texts)
#         except Exception:
#             pass

#     return ""


# def parse_description(soup: BeautifulSoup) -> str:
#     """Lấy mô tả / thành phần sản phẩm từ trang chi tiết."""
#     for sel in [
#         ".product-description",
#         ".tab-content .description",
#         "#product-description",
#         ".product-detail-content",
#         "[itemprop='description']",
#         ".product-info-detail",
#         ".product-content",
#     ]:
#         el = soup.select_one(sel)
#         if el:
#             return el.get_text(separator="\n", strip=True)
#     return ""


# def parse_comments(soup: BeautifulSoup) -> list[dict]:
#     """Lấy danh sách bình luận / đánh giá (nếu có)."""
#     comments = []
#     for review in soup.select(".review-item, .comment-item, [itemprop='review']"):
#         def _t(sel):
#             el = review.select_one(sel)
#             return el.get_text(strip=True) if el else ""

#         content = _t(".review-content, .content, [itemprop='reviewBody']")
#         if not content:
#             continue
#         comments.append({
#             "author":  _t(".review-author, .author, [itemprop='author']"),
#             "rating":  _t(".rating-value, [itemprop='ratingValue']"),
#             "content": content,
#             "date":    _t("time, .date, .review-date"),
#         })
#     return comments
def parse_breadcrumb(soup: BeautifulSoup) -> str:
    """Lấy danh mục từ mục 'Chi tiết sản phẩm' → div.product-specs-row[label=Danh mục]"""
    for row in soup.select("div.product-specs-row"):
        label = row.select_one("div.product-specs-label")
        if label and "Danh mục" in label.get_text():
            links = row.select("a.breadcrums-link")
            if links:
                return " > ".join(a.get_text(strip=True) for a in links)
    # fallback: breadcrumb nav
    items = soup.select("ul.breadcrumb-nav li")
    texts = [i.get_text(strip=True) for i in items if i.get_text(strip=True)]
    if texts and texts[0].lower() in ("trang chủ", "home"):
        texts = texts[1:]
    if len(texts) > 1:
        texts = texts[:-1]  # bỏ tên sản phẩm, chỉ lấy danh mục
    return " > ".join(texts)


def parse_description(soup: BeautifulSoup) -> str:
    """Lấy mô tả từ div#content-product bên trong div#product-detail"""
    el = soup.select_one("div#content-product")
    if el:
        return el.get_text(separator="\n", strip=True)
    # fallback
    el = soup.select_one("div#product-detail .tab-content")
    if el:
        return el.get_text(separator="\n", strip=True)
    return ""


def parse_comments(soup: BeautifulSoup) -> list[dict]:
    """
    Lấy comments từ div.main_show_comment.
    Mỗi review là div.d-flex.flex-col.gap8 chứa .nickname và span.content.comment-content
    """
    comments = []
    # Ưu tiên block ssr-comment-block (SSR, luôn có trong HTML tĩnh)
    # hoặc block .main_show_comment (AngularJS đã render)
    seen = set()

    for block in soup.select("div.main_show_comment"):
        for item in block.select("div.d-flex.flex-col.gap8"):
            author_el  = item.select_one("div.nickname")
            content_el = item.select_one("span.content.comment-content")
            if not content_el:
                continue
            content = content_el.get_text(strip=True)
            if not content or content in seen:
                continue
            seen.add(content)

            rating_el = item.select_one("span.ount-comment")
            rating = len(rating_el.select("span.star-on")) if rating_el else 0

            date_el = item.select_one("div.days.time")
            date = date_el.get_text(strip=True) if date_el else ""

            comments.append({
                "author":  author_el.get_text(strip=True) if author_el else "",
                "rating":  rating,
                "content": content,
                "date":    date,
            })

    return comments


def scrape_product_detail(stub: dict) -> dict:
    """
    Truy cập trang chi tiết sản phẩm → bổ sung category, description, comments.
    Trả về dict theo schema yêu cầu.
    """
    url  = stub["url"]
    soup = get_soup(url)

    # Fallback nếu không lấy được trang
    if not soup:
        return {
            "name":        stub["name"],
            "url":         url,
            "price":       stub["price"],
            "category":    "",
            "description": "",
            "comments":    [],
            "source":      "chiaki.vn",
        }

    # Tên đầy đủ từ h1 (listing đôi khi bị cắt)
    h1 = soup.select_one("h1.product-name, h1[itemprop='name'], h1")
    name = h1.get_text(strip=True) if h1 else stub["name"]

    # Giá (dùng lại từ listing nếu đã có)
    price = stub["price"]
    if not price:
        price_el = soup.select_one(".product-price, [itemprop='price']")
        if price_el:
            price = "".join(price_el.get_text(separator="", strip=True).split())

    return {
        "name":        name,
        "url":         url,
        "price":       price,
        "category":    parse_breadcrumb(soup),
        "description": parse_description(soup),
        "comments":    parse_comments(soup),
        "source":      "chiaki.vn",
    }

# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    # Bước 1: Thu thập URL + thông tin cơ bản
    log.info("=" * 60)
    log.info("BƯỚC 1: Thu thập danh sách sản phẩm")
    log.info("=" * 60)
    stubs = collect_product_stubs()
    log.info(f"\n✅ Tổng: {len(stubs)} sản phẩm\n")

    if not stubs:
        log.error("Không tìm thấy sản phẩm. Kiểm tra kết nối hoặc selector.")
        return

    # Bước 2: Crawl chi tiết từng sản phẩm
    log.info("=" * 60)
    log.info("BƯỚC 2: Crawl chi tiết sản phẩm")
    log.info("=" * 60)
    products = []

    for i, stub in enumerate(stubs, 1):
        log.info(f"[{i}/{len(stubs)}] {stub['url']}")
        try:
            product = scrape_product_detail(stub)
            products.append(product)
            log.info(f"  ✓ {product['name'][:65]}")
            log.info(f"    Giá: {product['price']} | Danh mục: {product['category'] or '(chưa xác định)'}")
        except Exception as e:
            log.error(f"  ✗ Lỗi: {e}")

        time.sleep(DELAY)

    # Bước 3: Lưu JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    log.info("=" * 60)
    log.info(f"💾 Đã lưu {len(products)} sản phẩm → '{OUTPUT_FILE}'")
    log.info("=" * 60)

    # In mẫu
    if products:
        print("\n📦 Mẫu sản phẩm đầu tiên:")
        sample = {}
        for k, v in products[0].items():
            if isinstance(v, str) and len(v) > 100:
                sample[k] = v[:100] + "..."
            else:
                sample[k] = v
        print(json.dumps(sample, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()