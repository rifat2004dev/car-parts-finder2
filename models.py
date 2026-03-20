from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Listing:
    search_query: str
    part_name: str
    car_model: str
    price: Optional[str]
    location: Optional[str]
    source: str
    url: str
    date_scraped: str

    @classmethod
    def create(
        cls,
        *,
        search_query: str,
        part_name: str,
        car_model: str,
        price: Optional[str],
        location: Optional[str],
        source: str,
        url: str,
    ) -> 'Listing':
        return cls(
            search_query=search_query,
            part_name=part_name.strip(),
            car_model=car_model.strip() or 'Unknown',
            price=(price or '').strip() or None,
            location=(location or '').strip() or None,
            source=source.strip(),
            url=url.strip(),
            date_scraped=datetime.utcnow().isoformat(timespec='seconds'),
        )
