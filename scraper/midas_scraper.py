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


class MidasScraper(BaseScraper):
    source_name = 'midas'
    base_url = 'https://midas.co.za'

    def scrape(self) -> list[Listing]:
        listings: list[Listing] = []
        seen: set[str] = set()

        for variant in query_variants(self.query):
            for page in range(1, MAX_PAGES_PER_SOURCE + 1):
                url = f'{self.base_url}/?s={quote_plus(variant)}&post_type=product&page={page}'
                response = self.get(url)
                soup = self.soup(response.text)
                cards = soup.select('li.product, .product, article.product')
                page_results = 0

                for card in cards:
                    if not isinstance(card, Tag):
                        continue

                    anchor = card.select_one('a[href]')
                    if not anchor:
                        continue
                    href = urljoin(self.base_url, anchor.get('href', '').strip())
                    if not is_http_url(href) or href in seen:
                        continue

                    title_node = card.select_one('h2, h3, .woocommerce-loop-product__title, .product-title')
                    title = title_node.get_text(' ', strip=True) if title_node else anchor.get_text(' ', strip=True)
                    if not title or not contains_query_keyword(title, self.query):
                        continue

                    text = card.get_text(' ', strip=True)
                    price = extract_price(text)
                    availability = 'In stock' if 'in stock' in text.lower() else None
                    location = 'South Africa - online / in-store'
                    if availability and price:
                        price = f'{price} ({availability})'
                    elif availability:
                        price = availability

                    listings.append(
                        Listing.create(
                            search_query=self.query,
                            part_name=title,
                            car_model=infer_car_model(title, self.query),
                            price=price,
                            location=location,
                            source='Midas',
                            url=href,
                        )
                    )
                    seen.add(href)
                    page_results += 1

                if page_results == 0:
                    break
                polite_delay()

            if listings:
                break

        return listings
