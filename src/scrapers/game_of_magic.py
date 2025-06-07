import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By


class GameOfMagicScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')
        product_selector = category.selectors.get('product_selector')

        if not self.wait_for_element(product_selector):
            self.logger.error(f"Couldn't find product container for category {category.name}")
            return []

        self.take_screenshot(f"{self.name}_{category.name}_listing.png")

        product_elements = self.driver.find_elements(By.XPATH, product_selector)
        self.logger.info(f"Found {len(product_elements)} products")

        product_urls = []
        for element in product_elements:
            try:
                url_elem = element.find_element(By.XPATH, urls_selector)
                title = url_elem.get_attribute('title') or url_elem.text.strip()
                url = url_elem.get_attribute('href')

                if title and url:
                    product_urls.append((title, url))
            except Exception as e:
                self.logger.warning(f"Error extracting product info: {e}")

        return product_urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}

        # Title
        try:
            title_selector = category.selectors.get('title_selector')
            if title_selector:
                title_element = self.driver.find_element(By.XPATH, title_selector)
                data['title'] = title_element.text.strip()
        except Exception:
            self.logger.warning("Title not found")

        # Price
        try:
            price_selector = category.selectors.get('price_selector')
            if price_selector:
                price_element = self.driver.find_element(By.XPATH, price_selector)
                price_text = price_element.text.strip()
                pattern = r'\d+(?:[\.,]\d+)?'
                match = re.search(pattern, price_text.replace(".", "").replace(",", "."))
                if match:
                    data['price'] = match.group()
                else:
                    self.logger.warning(f"Price not matched in: {price_text}")
        except Exception:
            self.logger.warning("Price not found")

        return data
