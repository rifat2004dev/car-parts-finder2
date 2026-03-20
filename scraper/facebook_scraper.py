from __future__ import annotations

import json
import pickle
import time
from pathlib import Path
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    CHROME_BINARY,
    CHROMEDRIVER_PATH,
    FACEBOOK_COOKIES_FILE,
    FACEBOOK_EMAIL,
    FACEBOOK_PASSWORD,
    FACEBOOK_SCROLL_PAUSE_SECONDS,
    FACEBOOK_SCROLL_ROUNDS,
    HEADLESS,
    SELENIUM_IMPLICIT_WAIT,
    SELENIUM_PAGE_LOAD_TIMEOUT,
)
from models import Listing
from scraper.base import BaseScraper
from utils import contains_query_keyword, infer_car_model, is_http_url, western_cape_relevant


class FacebookMarketplaceScraper(BaseScraper):
    source_name = 'facebook_marketplace'
    marketplace_base = 'https://www.facebook.com/marketplace/capetown/search/?query={query}'

    def _build_driver(self) -> webdriver.Chrome:
        options = Options()
        if HEADLESS:
            options.add_argument('--headless=new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1600,1200')
        options.add_argument('--lang=en-ZA')
        options.add_argument('--disable-notifications')
        if CHROME_BINARY:
            options.binary_location = CHROME_BINARY

        if CHROMEDRIVER_PATH:
            service = Service(CHROMEDRIVER_PATH)
        else:
            service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(SELENIUM_PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(SELENIUM_IMPLICIT_WAIT)
        return driver

    def _load_cookies(self, driver: webdriver.Chrome) -> bool:
        if not FACEBOOK_COOKIES_FILE:
            return False
        cookie_path = Path(FACEBOOK_COOKIES_FILE)
        if not cookie_path.exists():
            return False
        driver.get('https://www.facebook.com/')
        try:
            if cookie_path.suffix.lower() == '.json':
                cookies = json.loads(cookie_path.read_text(encoding='utf-8'))
            else:
                with cookie_path.open('rb') as file_handle:
                    cookies = pickle.load(file_handle)
            for cookie in cookies:
                cookie.pop('sameSite', None)
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    continue
            driver.refresh()
            return True
        except Exception:
            return False

    def _login_if_needed(self, driver: webdriver.Chrome) -> None:
        if self._load_cookies(driver):
            return
        if not FACEBOOK_EMAIL or not FACEBOOK_PASSWORD:
            self.logger.warning('Facebook credentials/cookies not configured; scraper may be blocked.')
            return
        driver.get('https://www.facebook.com/login')
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(FACEBOOK_EMAIL)
        driver.find_element(By.ID, 'pass').send_keys(FACEBOOK_PASSWORD)
        driver.find_element(By.NAME, 'login').click()
        time.sleep(5)

    def scrape(self) -> list[Listing]:
        try:
            driver = self._build_driver()
        except Exception as exc:
            self.logger.exception('Could not start Chrome WebDriver: %s', exc)
            return []

        results: list[Listing] = []
        try:
            self._login_if_needed(driver)
            url = self.marketplace_base.format(query=quote_plus(self.query))
            driver.get(url)

            for _ in range(FACEBOOK_SCROLL_ROUNDS):
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(FACEBOOK_SCROLL_PAUSE_SECONDS)

            WebDriverWait(driver, 12).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/marketplace/item/"]'))
            )
            anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/marketplace/item/"]')
            seen: set[str] = set()
            for anchor in anchors:
                href = anchor.get_attribute('href') or ''
                text = (anchor.text or '').strip()
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                title = lines[0] if lines else ''
                if href in seen or not is_http_url(href) or not title:
                    continue
                seen.add(href)
                if not contains_query_keyword(title, self.query):
                    continue
                price = next((line for line in lines if line.upper().startswith('R')), None)
                location = next((line for line in lines if western_cape_relevant(line)), 'Cape Town')
                if not western_cape_relevant(location):
                    continue
                results.append(
                    Listing.create(
                        search_query=self.query,
                        part_name=title,
                        car_model=infer_car_model(title, self.query),
                        price=price,
                        location=location,
                        source='Facebook Marketplace',
                        url=href,
                    )
                )
        except (TimeoutException, WebDriverException) as exc:
            self.logger.exception('Facebook Marketplace scrape failed: %s', exc)
        finally:
            driver.quit()
        return results
