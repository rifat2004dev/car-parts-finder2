from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import Tag

from config import MAX_PAGES_PER_SOURCE
from models import Listing
from scraper.base import BaseScraper
from utils import contains_query_keyword, infer_car_model, is_http_url, polite_delay, western_cape_relevant


class GumtreeScraper(BaseScraper):
    source_name = 'gumtree'
    base_url = 'https://www.gumtree.co.za'
    category_path = '/s-auto-parts-accessories/western-cape/v1c9026l3100001p{page}'

    def scrape(self) -> list[Listing]:
        listings: list[Listing] = []
        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            url = f'{self.base_url}{self.category_path.format(page=page)}?q={quote_plus(self.query)}'
            response = self.get(url)
            soup = self.soup(response.text)

            cards = soup.select('a[href*="/a-"]') or soup.select('a[href*="/v-"]') or soup.select('a[href]')
            if not cards:
                break

            page_results = 0
            for anchor in cards:
                if not isinstance(anchor, Tag):
                    continue
                title = anchor.get_text(' ', strip=True)
                href = urljoin(self.base_url, anchor.get('href', '').strip())
                if not title or not is_http_url(href) or not contains_query_keyword(title, self.query):
                    continue

                parent = anchor.find_parent(['div', 'article', 'li']) or anchor.parent
                parent_text = parent.get_text(' ', strip=True) if parent else title
                location = None
                for chunk in ['Cape Town', 'Bellville', 'Maitland', 'Paarl', 'Brackenfell', 'Western Cape']:
                    if chunk.lower() in parent_text.lower():
                        location = chunk
                        break

                if not western_cape_relevant(location or 'Western Cape'):
                    continue

                price = None
                for possible in ['Contact f/price', 'R']:
                    if possible.lower() in parent_text.lower():
                        idx = parent_text.lower().find(possible.lower())
                        price = parent_text[idx: idx + 25].strip()
                        break

                listings.append(
                    Listing.create(
                        search_query=self.query,
                        part_name=title,
                        car_model=infer_car_model(title, self.query),
                        price=price,
                        location=location or 'Western Cape',
                        source='Gumtree',
                        url=href,
                    )
                )
                page_results += 1

            if page_results == 0:
                break
            polite_delay()
        return listings
