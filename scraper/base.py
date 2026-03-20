from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT
from models import Listing
from utils import random_user_agent


class BaseScraper(ABC):
    source_name: str = 'base'

    def __init__(self, query: str):
        self.query = query
        self.logger = logging.getLogger(self.source_name)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random_user_agent(),
            'Accept-Language': 'en-ZA,en;q=0.9',
        })

    def get(self, url: str, **kwargs) -> requests.Response:
        response = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response

    def soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def scrape(self) -> list[Listing]:
        raise NotImplementedError

    def safe_scrape(self) -> list[Listing]:
        try:
            self.logger.info('Starting scrape for query=%s', self.query)
            results = self.scrape()
            self.logger.info('Finished scrape for query=%s results=%s', self.query, len(results))
            return results
        except Exception as exc:
            self.logger.exception('Scrape failed for %s: %s', self.source_name, exc)
            return []

    @staticmethod
    def compact_text(*parts: Iterable[str | None]) -> str:
        return ' '.join(str(p).strip() for p in parts if p and str(p).strip())
