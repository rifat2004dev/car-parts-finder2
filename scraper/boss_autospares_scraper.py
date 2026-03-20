from __future__ import annotations

from scraper.woocommerce_scraper import WooCommerceScraper


class BossAutoSparesScraper(WooCommerceScraper):
    source_name = 'boss_auto_spares'
    base_url = 'https://www.bossautospares.co.za'
    human_source = 'Boss Auto Spares'
    location_hint = 'Delivery to Cape Town / Western Cape'
