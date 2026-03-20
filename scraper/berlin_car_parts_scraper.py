from __future__ import annotations

from scraper.shopify_html_scraper import ShopifyHtmlScraper


class BerlinCarPartsScraper(ShopifyHtmlScraper):
    source_name = 'berlin_car_parts'
    base_url = 'https://www.berlincarparts.co.za'
    human_source = 'Berlin Car Parts'
    location_hint = 'Goodwood, Cape Town / Delivery to Western Cape'
