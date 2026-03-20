from __future__ import annotations

import logging
import random
import re
import time
from typing import Iterable, List
from urllib.parse import urlparse

from fake_useragent import UserAgent

from config import LOG_FILE, MAX_DELAY_SECONDS, MIN_DELAY_SECONDS, USER_AGENT, WESTERN_CAPE_KEYWORDS


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(),
        ],
    )


logger = logging.getLogger('car_part_scraper')


def random_user_agent() -> str:
    try:
        return UserAgent().random
    except Exception:
        return USER_AGENT


def polite_delay() -> None:
    time.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))


_non_alnum = re.compile(r'[^a-z0-9]+')
_price_re = re.compile(r'(R\s?[\d\s,.]+|Contact\s*f/?price)', re.I)


def normalize_text(value: str) -> str:
    return _non_alnum.sub(' ', (value or '').strip().lower()).strip()


def keywords_from_query(query: str) -> List[str]:
    return [token for token in normalize_text(query).split() if len(token) >= 3]


def query_variants(query: str) -> List[str]:
    words = keywords_from_query(query)
    if not words:
        return [query.strip()] if query.strip() else []

    variants: list[str] = []
    full = ' '.join(words)
    if full:
        variants.append(full)

    if len(words) >= 2:
        variants.append(f'{words[0]} {' '.join(words[1:])}')
        variants.append(f'{words[-1]} {' '.join(words[:-1])}')
        variants.append(' '.join(words[:2]))
        variants.append(' '.join(words[-2:]))

    if len(words) >= 3:
        variants.append(' '.join([words[0], words[-1]]))

    variants.append(words[0])

    output: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        variant = ' '.join(variant.split())
        if variant and variant not in seen:
            seen.add(variant)
            output.append(variant)
    return output


def is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)
    except Exception:
        return False


def extract_price(text: str) -> str | None:
    match = _price_re.search(text or '')
    return match.group(1).strip() if match else None


def infer_car_model(title: str, query: str) -> str:
    normalized_title = normalize_text(title)
    qwords = keywords_from_query(query)
    if len(qwords) <= 1:
        return 'Unknown'
    guess = ' '.join(qwords[1:])
    return guess.title() if guess and guess in normalized_title else 'Unknown'


def contains_query_keyword(title: str, query: str) -> bool:
    title_n = normalize_text(title)
    return any(word in title_n for word in keywords_from_query(query))


def western_cape_relevant(location: str | None) -> bool:
    if not location:
        return True
    loc = normalize_text(location)
    delivery_markers = [
        'delivery to western cape',
        'delivery to cape town',
        'western cape delivery',
        'cape town delivery',
        'goodwood',
        'salt river',
        'delivery',
        'shipping',
        'collection',
        'pickup',
        'nationwide',
    ]
    if any(marker in loc for marker in delivery_markers):
        return True
    return any(k in loc for k in WESTERN_CAPE_KEYWORDS)


def dedupe_by_url(items: Iterable) -> list:
    seen: set[str] = set()
    output = []
    for item in items:
        key = getattr(item, 'url', '').strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def format_results_table(rows: list[dict]) -> str:
    if not rows:
        return 'No parts found for this query.'

    headers = ['SOURCE', 'PART', 'PRICE', 'LOCATION', 'LINK']
    matrix = [headers] + [
        [
            row.get('source', ''),
            row.get('part_name', ''),
            row.get('price', '') or 'N/A',
            row.get('location', '') or 'N/A',
            row.get('url', ''),
        ]
        for row in rows
    ]
    widths = [max(len(str(r[i])) for r in matrix) for i in range(len(headers))]

    def fmt(line: list[str]) -> str:
        return ' | '.join(str(cell).ljust(widths[i]) for i, cell in enumerate(line))

    sep = '-+-'.join('-' * width for width in widths)
    return '\n'.join([fmt(matrix[0]), sep] + [fmt(r) for r in matrix[1:]])
