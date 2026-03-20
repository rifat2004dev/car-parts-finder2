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
