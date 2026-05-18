from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse
from collections import deque


class WebCrawler:
    def __init__(self, entrypoint, max_depth=2, max_pages=20, include_external=False):
        self.entrypoint = self.normalize_url(entrypoint)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.include_external = include_external

        self.base_domain = urlparse(self.entrypoint).netloc
        self.visited = set()
        self.crawled_urls = []

        self.validate_input()

    def validate_input(self):
        if self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")

        if self.max_pages <= 0:
            raise ValueError("max_pages must be greater than 0")

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url._replace(fragment="").geturl()

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"]

    def is_same_domain(self, url):
        return urlparse(url).netloc == self.base_domain

    def fetch_html(self, url):
        """
        Fetch HTML content from URL.
        Return None if request fails or content is not HTML.
        """
        print(f"\n[FETCHING] Đang tải URL: {url}")
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urlopen(request, timeout=10) as response:
                content_type = response.headers.get("Content-Type", "")
                print(f"[INFO] Content-Type: {content_type}")
                if "text/html" not in content_type:
                    print("[SKIP] URL này không phải HTML, bỏ qua.")
                    return None
                html = response.read().decode("utf-8", errors="ignore")
                print(f"[SUCCESS] Tải thành công HTML, độ dài: {len(html)} ký tự")

                return html

        except Exception as error:
            print(f"[ERROR] Không tải được URL: {url}")
            print(f"[ERROR] Lý do: {error}")
            return None

    def extract_links(self, html, current_url):
        """
        Extract all links from HTML using BeautifulSoup.
        Convert relative URLs to absolute URLs.
        """
        print(f"[PARSING] Đang phân tích HTML từ: {current_url}")

        soup = BeautifulSoup(html, "html.parser")
        links = []

        total_a_tags = 0
        skipped_invalid = 0
        skipped_external = 0

        for tag in soup.find_all("a"):
            total_a_tags += 1

            href = tag.get("href")

            if not href:
                skipped_invalid += 1
                continue

            absolute_url = urljoin(current_url, href)
            absolute_url = self.normalize_url(absolute_url)

            if not self.is_valid_url(absolute_url):
                skipped_invalid += 1
                continue

            if not self.include_external and not self.is_same_domain(absolute_url):
                skipped_external += 1
                continue

            links.append(absolute_url)

        print(f"[RESULT] Tổng thẻ <a> tìm thấy: {total_a_tags}")
        print(f"[RESULT] Link hợp lệ lấy được: {len(links)}")
        print(f"[SKIP] Link không hợp lệ: {skipped_invalid}")
        print(f"[SKIP] Link ngoài domain: {skipped_external}")

        return links

    def crawl(self):
        """
        Crawl URLs from entrypoint using BFS.
        """
        print("========== START CRAWLING ==========")
        print(f"Entrypoint        : {self.entrypoint}")
        print(f"Base domain       : {self.base_domain}")
        print(f"Max depth         : {self.max_depth}")
        print(f"Max pages         : {self.max_pages}")
        print(f"Include external  : {self.include_external}")
        print("====================================")

        queue = deque()
        queue.append((self.entrypoint, 0))

        while queue and len(self.crawled_urls) < self.max_pages:
            current_url, current_depth = queue.popleft()

            print("\n------------------------------------")
            print(f"[QUEUE] Số URL đang chờ crawl: {len(queue)}")
            print(f"[CURRENT] URL hiện tại: {current_url}")
            print(f"[DEPTH] Độ sâu hiện tại: {current_depth}")
            print(f"[CRAWLED] Số trang đã crawl: {len(self.crawled_urls)} / {self.max_pages}")

            if current_url in self.visited:
                print("[SKIP] URL đã được crawl trước đó.")
                continue

            if current_depth > self.max_depth:
                print("[SKIP] URL vượt quá max_depth.")
                continue

            self.visited.add(current_url)
            self.crawled_urls.append(current_url)

            html = self.fetch_html(current_url)

            if html is None:
                print("[SKIP] Không có HTML để parse.")
                continue

            links = self.extract_links(html, current_url)

            added_to_queue = 0

            for link in links:
                if link not in self.visited:
                    queue.append((link, current_depth + 1))
                    added_to_queue += 1

            print(f"[QUEUE] Đã thêm vào queue: {added_to_queue} link")
            print(f"[VISITED] Tổng URL đã visited: {len(self.visited)}")

        print("\n========== FINISHED CRAWLING ==========")
        print(f"Tổng số trang crawl được: {len(self.crawled_urls)}")
        print(f"Tổng số URL visited: {len(self.visited)}")
        print("=======================================")

        return self.crawled_urls


def main():
    crawler = WebCrawler(
        entrypoint="https://chiaki.vn/",
        max_depth=2,
        max_pages=10,
        include_external=False
    )

    urls = crawler.crawl()

    print("\nCrawled URLs:")
    for index, url in enumerate(urls, start=1):
        print(f"{index}. {url}")


if __name__ == "__main__":
    main()