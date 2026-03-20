from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import Tag

from config import MAX_PAGES_PER_SOURCE
from models import Listing
from scraper.base import BaseScraper
from utils import contains_query_keyword, infer_car_model, is_http_url, polite_delay


class MasterpartsScraper(BaseScraper):
    source_name = 'masterparts'
    base_url = 'https://www.masterparts.com'

    def scrape(self) -> list[Listing]:
        """
        Best-effort scraper against the public site search.
        Masterparts does not expose a simple public JSON search API, so this scraper
        targets the HTML search results page.
        """
        listings: list[Listing] = []
        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            url = f'{self.base_url}/?s={quote_plus(self.query)}&paged={page}'
            response = self.get(url)
            soup = self.soup(response.text)
            cards = soup.select('article a[href]') or soup.select('h2 a[href]') or soup.select('a[href]')
            page_results = 0
            for anchor in cards:
                if not isinstance(anchor, Tag):
                    continue
                title = anchor.get_text(' ', strip=True)
                href = urljoin(self.base_url, anchor.get('href', '').strip())
                if not title or not is_http_url(href) or not contains_query_keyword(title, self.query):
                    continue
                if '/branches/' in href or '/blog/' in href:
                    continue

                parent = anchor.find_parent(['article', 'div', 'li']) or anchor.parent
                parent_text = parent.get_text(' ', strip=True) if parent else title
                listings.append(
                    Listing.create(
                        search_query=self.query,
                        part_name=title,
                        car_model=infer_car_model(title, self.query),
                        price=None,
                        location='Western Cape',
                        source='Masterparts',
                        url=href,
                    )
                )
                page_results += 1
            if page_results == 0:
                break
            polite_delay()
        return listings
