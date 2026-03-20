from __future__ import annotations

from scraper.shopify_html_scraper import ShopifyHtmlScraper


class AtlanticAutoSparesScraper(ShopifyHtmlScraper):
    source_name = 'atlantic_auto_spares'
    base_url = 'https://www.atlanticauto.co.za'
    human_source = 'Atlantic Auto Spares'
    location_hint = 'Delivery to Western Cape'
