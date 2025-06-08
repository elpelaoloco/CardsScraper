import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
import re

class ElReinoScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get("page_load_delay", 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        container_xpath = "//div[contains(@class, 'product-element-bottom')]"
        self.wait_for_element(container_xpath)
        containers = self.driver.find_elements(By.XPATH, container_xpath)
        urls = []

        for container in containers:
            try:
                a_tag = container.find_element(By.XPATH, ".//a[contains(@href, '/producto/')]")
                url = a_tag.get_attribute("href")
                name = a_tag.text.strip()

                if name and url:
                    urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error extracting URL or name: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        time.sleep(self.config.get("page_load_delay", 2))

        data = {}

        # Nombre desde h1
        try:
            title_element = self.driver.find_element(By.XPATH, "//h1")
            data["name"] = title_element.text.strip()
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        # Precio con descuento (si lo hay)
        try:
            price_element = self.driver.find_element(By.XPATH, ".//ins//span[contains(@class, 'woocommerce-Price-amount')]")
            price_text = price_element.text.strip()
            price_text = price_text.replace(".", "").replace(",", ".")  # Normalizar
            match = re.search(r"\d+(?:\.\d+)?", price_text)
            data["price"] = match.group() if match else price_text
        except Exception as e:
            self.logger.warning(f"Price not found: {e}")
            data["price"] = ""

        return data