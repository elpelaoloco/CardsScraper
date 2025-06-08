import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class GuildDreamsScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))
    
    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')
        
        if not self.wait_for_element(urls_selector):
            self.logger.error(f"Couldn't find title elements for category {category.name}")
            return []
        
        self.take_screenshot(f"{self.name}_{category.name}_listing.png")
        
        elements = self.driver.find_elements(By.XPATH, urls_selector)
        self.logger.info(f"Found {len(elements)} title elements")
        
        product_urls = []
        for element in elements:
            try:
                title = element.text.strip()
                url = element.get_attribute('href')
                
                if title and url:
                    product_urls.append((title, url))
            except Exception as e:
                self.logger.warning(f"Error extracting element data: {e}")
        
        return product_urls
    
    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}

        # Nombre (title_selector obligatorio)
        title_selector = category.selectors.get('title_selector')
        try:
            if title_selector:
                title_element = self.driver.find_element(By.XPATH, title_selector)
                data['name'] = title_element.text.strip()
            else:
                self.logger.warning("Title selector not defined")
                data['name'] = "unknown"
        except Exception:
            self.logger.warning("Name element not found")
            data['name'] = "unknown"

        # Precio
        price_selector = category.selectors.get('price_selector')
        try:
            if price_selector:
                price_element = self.driver.find_element(By.XPATH, price_selector)
                price_text = price_element.text.strip()
                pattern = r'\b\d+(?:[.,]\d{3})*(?:[.,]\d{2})?\b'
                match = re.search(pattern, price_text.replace('.', '').replace(',', '.'))
                data['price'] = match.group() if match else price_text
            else:
                self.logger.warning("Price selector not defined")
                data['price'] = "unknown"
        except Exception:
            self.logger.warning("Price element not found")
            data['price'] = "unknown"

        # Stock (opcional)
        stock_selector = category.selectors.get('stock_selector')
        if stock_selector:
            try:
                stock_element = self.driver.find_element(By.XPATH, stock_selector)
                data['stock'] = stock_element.text.strip()
            except Exception:
                self.logger.warning("Stock element not found")

        # Descripción (opcional)
        description_selector = category.selectors.get('description_selector')
        if description_selector:
            try:
                description_element = self.driver.find_element(By.XPATH, description_selector)
                data['description'] = description_element.text.strip()
            except Exception:
                self.logger.warning("Description element not found")

        # Idioma (opcional, extraído desde descripción)
        language_selector = category.selectors.get('language_selector')
        if language_selector and 'description' in data:
            try:
                pattern = r"Idioma:\s*([^\n\.]+)\."
                match = re.search(pattern, data['description'])
                data['language'] = match.group(1) if match else 'unknown'
            except Exception:
                self.logger.warning("Error extracting language")
                data['language'] = "unknown"

        return data
