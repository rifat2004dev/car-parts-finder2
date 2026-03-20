from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
DB_PATH = BASE_DIR / 'car_parts.db'
LOG_FILE = LOG_DIR / 'scraper.log'
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '600'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '25'))
MIN_DELAY_SECONDS = float(os.getenv('MIN_DELAY_SECONDS', '1.0'))
MAX_DELAY_SECONDS = float(os.getenv('MAX_DELAY_SECONDS', '2.5'))
MAX_PAGES_PER_SOURCE = int(os.getenv('MAX_PAGES_PER_SOURCE', '3'))
USER_AGENT = os.getenv(
    'USER_AGENT',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
)

WESTERN_CAPE_KEYWORDS = [
    'western cape', 'cape town', 'bellville', 'montague gardens', 'maitland',
    'paarl', 'brackenfell', 'strand', 'kenilworth', 'milnerton', 'goodwood',
    'wellington', 'somerset west', 'stellenbosch', 'claremont', 'blouberg',
]

FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')
FACEBOOK_COOKIES_FILE = os.getenv('FACEBOOK_COOKIES_FILE', '')
CHROME_BINARY = os.getenv('CHROME_BINARY', '')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
SELENIUM_PAGE_LOAD_TIMEOUT = int(os.getenv('SELENIUM_PAGE_LOAD_TIMEOUT', '40'))
SELENIUM_IMPLICIT_WAIT = int(os.getenv('SELENIUM_IMPLICIT_WAIT', '3'))
FACEBOOK_SCROLL_ROUNDS = int(os.getenv('FACEBOOK_SCROLL_ROUNDS', '6'))
FACEBOOK_SCROLL_PAUSE_SECONDS = float(os.getenv('FACEBOOK_SCROLL_PAUSE_SECONDS', '2.0'))
