from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import Tag

from config import MAX_PAGES_PER_SOURCE
from models import Listing
from scraper.base import BaseScraper
from utils import contains_query_keyword, extract_price, infer_car_model, is_http_url, polite_delay, query_variants


class WooCommerceScraper(BaseScraper):
    base_url: str = ''
    human_source: str = ''
    location_hint: str = 'Delivery to Western Cape'

    def scrape(self) -> list[Listing]:
        listings: list[Listing] = []
        seen: set[str] = set()
        for variant in query_variants(self.query):
            total_hits = 0
            for page in range(1, MAX_PAGES_PER_SOURCE + 1):
                url = f'{self.base_url}/?s={quote_plus(variant)}&post_type=product&page={page}'
                response = self.get(url)
                soup = self.soup(response.text)
                cards = soup.select('li.product, article.product, .product, .type-product')
                page_hits = 0
                for card in cards:
                    if not isinstance(card, Tag):
                        continue
                    anchor = card.select_one('a[href]')
                    if not anchor:
                        continue
                    href = urljoin(self.base_url, anchor.get('href', '').strip())
                    if not is_http_url(href) or href in seen or '?s=' in href:
                        continue
                    title_node = card.select_one('h2, h3, .woocommerce-loop-product__title, .product-title')
                    title = title_node.get_text(' ', strip=True) if title_node else anchor.get_text(' ', strip=True)
                    if not title or not contains_query_keyword(title, self.query):
                        continue
                    listings.append(
                        Listing.create(
                            search_query=self.query,
                            part_name=title,
                            car_model=infer_car_model(title, self.query),
                            price=extract_price(card.get_text(' ', strip=True)),
                            location=self.location_hint,
                            source=self.human_source,
                            url=href,
                        )
                    )
                    seen.add(href)
                    page_hits += 1
                total_hits += page_hits
                if page_hits == 0:
                    break
                polite_delay()
            if total_hits:
                break
        return listings
