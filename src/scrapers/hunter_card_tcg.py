import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class HunterCardTCG(BaseScraper):
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
                if url and not title:
                    title = url.split('/')[-1].replace('-', ' ').capitalize()
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

        # Nombre
        try:
            name_element = self.driver.find_element(By.XPATH, "//h1[contains(@class,'product_title')]")
            data["name"] = name_element.text.strip()
        except NoSuchElementException:
            self.logger.warning("Name element not found")
            data["name"] = "unknown"
        
        # Precio
        try:
            price_selector = category.selectors.get('price_selector')
            price_element = self.driver.find_element(By.XPATH, price_selector)
            price_text = price_element.text.strip()
            pattern = r'\d+(?:[.,]\d+)?'
            match = re.search(pattern, price_text.replace('.', '').replace(',', '.'))
            data["price"] = match.group() if match else "unknown"
        except NoSuchElementException:
            self.logger.warning("Price element not found")
            data["price"] = "unknown"

        # Stock (opcional)
        try:
            stock_selector = category.selectors.get("stock_selector")
            if stock_selector:
                stock_element = self.driver.find_element(By.XPATH, stock_selector)
                data["stock"] = stock_element.text.strip()
        except NoSuchElementException:
            pass

        # Descripción
        try:
            desc_selector = category.selectors.get("description_selector")
            if desc_selector:
                desc_element = self.driver.find_element(By.XPATH, desc_selector)
                data["description"] = desc_element.text.strip()
        except NoSuchElementException:
            pass

        # Idioma
        try:
            lang_selector = category.selectors.get("language_selector")
            if lang_selector:
                lang_element = self.driver.find_element(By.XPATH, lang_selector)
                pattern = r"[–-]\s*([^\s\n]+)"
                matches = re.findall(pattern, lang_element.text)
                data['language'] = matches[-1] if matches else "unknown"
        except NoSuchElementException:
            data["language"] = "unknown"
        image_selector = category.selectors.get("image_selector")
        try:
            if image_selector:
                image_el = self.driver.find_element(By.XPATH, image_selector)
                data["img_url"] = image_el.get_attribute("src")
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"Image not found: {e}")
            data["img_url"] = ""


        return data
