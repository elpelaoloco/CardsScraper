import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
import re
import traceback

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
            alternative_price = self.extract_price()
            if alternative_price:
                print(f"Alternative price found: {alternative_price}")
            data["price"] = alternative_price
        except Exception as e:
            traceback.print_exc()
            self.logger.warning(f"Price not found: {e}")
            data["price"] = ""
        image_selector = category.selectors.get("image_selector")
        try:
            if image_selector:
                image_el = self.driver.find_element(By.XPATH, image_selector)
                img_url = image_el.get_attribute("src")
                if img_url and not img_url.startswith("data:image"):
                    data["img_url"] = img_url
                else:
                    data["img_url"] = ""
                    self.logger.warning("Fallback image or empty URL encountered")
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"Image not found: {e}")
            data["img_url"] = ""

        return data
    
    def extract_price(self) -> str:
        price_element = self.driver.find_elements(By.XPATH, "//p[@class='price']/span")
        if not price_element:
            self.logger.warning("Price element not found")
            return ""
        
        span_descendants = price_element

        if len(span_descendants) == 1:
            text = span_descendants[0].get_attribute("innerText")
            match =re.search(r'[\d.,]+', text)
            if match:
                print(f"Matched text: {match}")
                matched_text = match.group(0)
                return matched_text
            else:
                self.logger.warning("No valid price found in the text")
                return ""
        else:
            for span in span_descendants:
                if 'actual' in span.get_attribute("innerText").lower():
                    text = span.get_attribute("innerText")
                    match =re.search(r'[\d.,]+', text)
                    if match:
                        print(f"Matched text: {match}")
                        matched_text = match.group(0)
                        return matched_text
