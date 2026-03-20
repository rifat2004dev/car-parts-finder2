from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Iterable

from config import CACHE_TTL_SECONDS, DB_PATH
from models import Listing

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_query TEXT NOT NULL,
    part_name TEXT NOT NULL,
    car_model TEXT,
    price TEXT,
    location TEXT,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date_scraped TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_listings_query ON listings(search_query);
CREATE INDEX IF NOT EXISTS idx_listings_date ON listings(date_scraped);
CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history(query);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


class Database:
    def initialize(self) -> None:
        with get_conn() as conn:
            conn.executescript(SCHEMA)

    def add_search_history(self, query: str) -> None:
        with get_conn() as conn:
            conn.execute(
                'INSERT INTO search_history(query, timestamp) VALUES (?, ?)',
                (query, datetime.utcnow().isoformat(timespec='seconds')),
            )

    def get_cached_results(self, query: str) -> list[sqlite3.Row]:
        cutoff = (datetime.utcnow() - timedelta(seconds=CACHE_TTL_SECONDS)).isoformat(timespec='seconds')
        with get_conn() as conn:
            rows = conn.execute(
                'SELECT search_query, part_name, car_model, price, location, source, url, date_scraped '
                'FROM listings WHERE search_query = ? AND date_scraped >= ? ORDER BY date_scraped DESC',
                (query, cutoff),
            ).fetchall()
        return list(rows)

    def insert_listings(self, listings: Iterable[Listing]) -> int:
        inserted = 0
        with get_conn() as conn:
            for item in listings:
                cur = conn.execute(
                    'INSERT OR IGNORE INTO listings(search_query, part_name, car_model, price, location, source, url, date_scraped) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (
                        item.search_query,
                        item.part_name,
                        item.car_model,
                        item.price,
                        item.location,
                        item.source,
                        item.url,
                        item.date_scraped,
                    ),
                )
                inserted += cur.rowcount
        return inserted

    def rows_to_dicts(self, rows: Iterable[sqlite3.Row]) -> list[dict]:
        return [dict(r) for r in rows]
