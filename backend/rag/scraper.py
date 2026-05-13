import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebScraper:
    def __init__(self, max_pages=10):
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

    def _extract_links(self, soup, base_url):
        links = set()
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            # Only follow same domain, skip anchors/files
            if (self._same_domain(href, base_url) and
                "#" not in href and
                not href.endswith((".pdf", ".jpg", ".png", ".zip"))):
                links.add(href.split("?")[0])  # remove query params
        return links

    def _scrape_single(self, url):
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer",
                             "header", "aside", "noscript", "iframe",
                             "form", "button", "input"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title else url
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            clean_lines = [line for line in lines if len(line) > 30]
            clean_text = "\n".join(clean_lines)

            return soup, {
                "url": url,
                "title": title,
                "text": clean_text,
                "success": bool(clean_text),
                "error": None if clean_text else "No content extracted"
            }
        except Exception as e:
            return None, {"url": url, "title": "", "text": "",
                         "success": False, "error": str(e)}

    def scrape_url(self, url: str) -> dict:
        """Scrape a single URL — keeps backward compatibility"""
        _, result = self._scrape_single(url)
        return result

    def scrape_site(self, start_url: str) -> list:
        """
        Scrape start_url + all linked pages on the same domain.
        Returns list of page dicts.
        """
        visited = set()
        to_visit = {start_url}
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

            time.sleep(0.5)  # be polite

        return results

    def scrape_multiple(self, urls: list) -> list:
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
            time.sleep(1)
        return results