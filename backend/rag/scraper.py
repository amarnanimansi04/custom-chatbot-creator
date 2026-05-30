import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebScraper:
    def __init__(self, max_pages=500):
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _same_domain(self, url, base_url):
        return urlparse(url).netloc == urlparse(base_url).netloc

    # URL path segments to skip — irrelevant to business content
    SKIP_PATTERNS = [
        "/blogs/", "/blog/", "/cdn-cgi/", "/wp-", "/tag/", "/author/",
        "/page/", "/feed/", "/rss/", "/sitemap", "/login", "/register",
        "/cart", "/checkout", "/account", "/search"
    ]

    def _should_skip(self, url):
        return any(pattern in url for pattern in self.SKIP_PATTERNS)

    def _extract_links(self, soup, base_url):
        links = set()
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            if (self._same_domain(href, base_url) and
                "#" not in href and
                not href.endswith((".pdf", ".jpg", ".png", ".zip")) and
                not self._should_skip(href)):
                links.add(href.split("?")[0])
        return links

    def _scrape_with_playwright(self, url):
        """Use headless browser to render JavaScript-heavy pages."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)
                # Extra wait for JS-rendered content (package listings etc.)
                page.wait_for_timeout(4000)
                html = page.content()
                browser.close()
            return html
        except Exception as e:
            print(f"Playwright failed for {url}: {e}")
            return None

    def _parse_html(self, html, url):
        """Parse HTML and return (soup_for_links, title, clean_text)."""
        soup = BeautifulSoup(html, "html.parser")
        link_soup = BeautifulSoup(html, "html.parser")  # separate copy for links

        title = soup.title.string.strip() if soup.title else url

        # Remove non-content tags (keep nav/footer in link_soup for link extraction)
        for tag in soup(["script", "style", "noscript", "iframe", "form", "button", "input"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        # Keep lines > 5 chars so phone numbers, emails, prices aren't lost
        clean_lines = [line for line in lines if len(line) > 5]
        clean_text = "\n".join(clean_lines)

        return link_soup, title, clean_text

    def _scrape_single(self, url):
        html = None

        # Try Playwright first (handles JS-rendered content)
        html = self._scrape_with_playwright(url)

        # Fall back to requests if Playwright fails
        if not html:
            try:
                response = self.session.get(url, timeout=15, allow_redirects=True)
                response.raise_for_status()
                html = response.text
            except Exception as e:
                return None, {"url": url, "title": "", "text": "", "success": False, "error": str(e)}

        try:
            link_soup, title, clean_text = self._parse_html(html, url)
            return link_soup, {
                "url": url,
                "title": title,
                "text": clean_text,
                "success": bool(clean_text),
                "error": None if clean_text else "No content extracted"
            }
        except Exception as e:
            return None, {"url": url, "title": "", "text": "", "success": False, "error": str(e)}

    def scrape_url(self, url: str) -> dict:
        """Scrape a single URL — keeps backward compatibility"""
        _, result = self._scrape_single(url)
        return result

    def scrape_site(self, start_url: str, seed_urls: list = None) -> list:
        """
        Scrape start_url + all linked pages on the same domain.
        seed_urls: extra URLs to always include at the start of the queue.
        Returns list of page dicts.
        """
        visited = set()
        to_visit = set(seed_urls) if seed_urls else {start_url}
        to_visit.add(start_url)
        results = []

        while to_visit and len(visited) < self.max_pages:
            url = to_visit.pop()
            if url in visited:
                continue
            visited.add(url)

            print(f"Scraping: {url}")
            soup, result = self._scrape_single(url)
            if result["success"]:
                results.append(result)
                if soup:
                    new_links = self._extract_links(soup, start_url)
                    to_visit.update(new_links - visited)

            time.sleep(1)  # be polite

        print(f"Scraped {len(results)} pages total.")
        return results

    def scrape_multiple(self, urls: list) -> list:
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
            time.sleep(1)
        return results
