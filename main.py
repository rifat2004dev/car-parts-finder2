from __future__ import annotations

import argparse
import logging
from dataclasses import asdict
from typing import Iterable

from database import Database
from models import Listing
from scraper import SCRAPER_REGISTRY
from utils import (
    contains_query_keyword,
    dedupe_by_url,
    format_results_table,
    is_http_url,
    logger,
    setup_logging,
    western_cape_relevant,
)


def validate_listing(item: Listing, query: str) -> bool:
    if not item.part_name.strip():
        return False
    if not is_http_url(item.url):
        return False
    if not contains_query_keyword(item.part_name, query):
        return False
    if item.location and not western_cape_relevant(item.location):
        return False
    return True


class SearchService:
    def __init__(self) -> None:
        self.db = Database()
        self.db.initialize()

    def search(self, query: str, use_cache: bool = True) -> list[dict]:
        self.db.add_search_history(query)

        if use_cache:
            cached = self.db.get_cached_results(query)
            if cached:
                logger.info('Using cached results for query=%s count=%s', query, len(cached))
                return self.db.rows_to_dicts(cached)

        collected: list[Listing] = []
        for scraper_cls in SCRAPER_REGISTRY:
            scraper = scraper_cls(query)
            results = scraper.safe_scrape()
            valid = [item for item in results if validate_listing(item, query)]
            collected.extend(valid)

        deduped = dedupe_by_url(collected)
        inserted = self.db.insert_listings(deduped)
        logger.info('Inserted %s new listings for query=%s', inserted, query)
        return [asdict(item) for item in deduped]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Search Western Cape car parts and delivery-eligible South African listings from multiple websites.')
    parser.add_argument('query', help='Example: "radiator polo vivo"')
    parser.add_argument('--no-cache', action='store_true', help='Ignore the 10 minute cache and scrape live.')
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()
    service = SearchService()
    try:
        results = service.search(args.query.strip(), use_cache=not args.no_cache)
        print(format_results_table(results))
    except KeyboardInterrupt:
        logging.getLogger(__name__).warning('Interrupted by user.')


if __name__ == '__main__':
    main()
