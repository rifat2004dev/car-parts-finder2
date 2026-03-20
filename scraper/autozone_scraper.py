from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import Tag

from config import MAX_PAGES_PER_SOURCE
from models import Listing
from scraper.base import BaseScraper
from utils import (
    contains_query_keyword,
    extract_price,
    infer_car_model,
    is_http_url,
    polite_delay,
    query_variants,
)


class AutoZoneScraper(BaseScraper):
    source_name = 'autozone_online'
    base_url = 'https://www.autozoneonline.co.za'

    def _extract_from_container(self, container: Tag, href: str) -> Listing | None:
        text = container.get_text(' ', strip=True)
        title = ''

        # Prefer strong title selectors first.
        for selector in [
            'h1',
            'h2',
            'h3',
            '.product-title',
            '.product-name',
            '.card-title',
            'a[title]',
        ]:
            node = container.select_one(selector)
            if node:
                title = node.get_text(' ', strip=True)
                break

        if not title:
            links = [a for a in container.select('a[href]') if '/search/' not in a.get('href', '')]
            for link in links:
                candidate = link.get_text(' ', strip=True)
                if len(candidate) >= 8:
                    title = candidate
                    break

        title = title.strip()
        if not title or not contains_query_keyword(title, self.query):
            return None

        price = extract_price(text)
        location = 'South Africa - branch collection'

        return Listing.create(
            search_query=self.query,
            part_name=title,
            car_model=infer_car_model(title, self.query),
            price=price,
            location=location,
            source='AutoZone',
            url=href,
        )

    def _scrape_search_url(self, url: str) -> list[Listing]:
        response = self.get(url)
        soup = self.soup(response.text)
        results: list[Listing] = []
        seen: set[str] = set()

        containers = soup.select(
            'li.product, article.product, .product-item, .product, .item-box, .product-grid-item, .search-result'
        )

        # Fallback for sites with flatter markup.
        if not containers:
            containers = [a.find_parent(['div', 'li', 'article']) or a for a in soup.select('a[href]')]

        for container in containers:
            if not isinstance(container, Tag):
                continue

            href = ''
            for anchor in container.select('a[href]'):
                candidate = urljoin(self.base_url, anchor.get('href', '').strip())
                if not is_http_url(candidate):
                    continue
                if candidate.startswith(f'{self.base_url}/search/'):
                    continue
                if candidate == self.base_url or candidate.rstrip('/') == self.base_url:
                    continue
                href = candidate
                break

            if not href or href in seen:
                continue
            seen.add(href)

            item = self._extract_from_container(container, href)
            if item:
                results.append(item)

        return results

    def scrape(self) -> list[Listing]:
        listings: list[Listing] = []
        seen_urls: set[str] = set()
        variants = query_variants(self.query)

        for variant in variants:
            for page in range(1, MAX_PAGES_PER_SOURCE + 1):
                search_url = (
                    f'{self.base_url}/search/text/keyword?k={quote_plus(variant)}&q=&pagenumber={page}'
                )
                page_results = self._scrape_search_url(search_url)
                new_items = [item for item in page_results if item.url not in seen_urls]
                for item in new_items:
                    seen_urls.add(item.url)
                listings.extend(new_items)
                if not page_results:
                    break
                polite_delay()
            if listings:
                break

        return listings
