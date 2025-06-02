# src/scrapers/la_comarca.py
import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By

class LaComarcaScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        selector = category.selectors.get('urls_selector')
        self.wait_for_element(selector)

        elements = self.driver.find_elements(By.XPATH, selector)
        urls = []
        for el in elements:
            try:
                name = el.text.strip()
                url = el.get_attribute('href')
                if name and url:
                    urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error extracting URL: {e}")
        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}
        price_sel = category.selectors.get('price_selector')
        if price_sel:
            try:
                price_el = self.driver.find_element(By.XPATH, price_sel)
                data["price"] = price_el.text.strip()
            except Exception as e:
                self.logger.warning(f"No price found: {e}")

        return data
