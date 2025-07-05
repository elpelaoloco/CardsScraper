import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GuildDreamsScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_to_image: Dict[str, str] = {}

    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def wait_for_valid_image(driver, xpath, timeout=5):
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                el = driver.find_element(By.XPATH, xpath)
                src = el.get_attribute("data-src") or el.get_attribute("src")
                if src and not src.startswith("data:image"):
                    return src
            except:
                pass
            time.sleep(0.5)
        return ""

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')
        image_selector = category.selectors.get('image_selector')

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

                # Buscar imagen desde el elemento padre
                try:
                    container = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'bs-product')]")
                    img_el = container.find_element(By.XPATH, ".//img")
                    img_url = img_el.get_attribute("data-src") or img_el.get_attribute("src")
                    if not img_url or img_url.startswith("data:image"):
                        img_url = ""
                    self.url_to_image[url] = img_url
                except Exception:
                    self.url_to_image[url] = ""

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

        # Stock
        stock_selector = category.selectors.get('stock_selector')
        if stock_selector:
            try:
                stock_element = self.driver.find_element(By.XPATH, stock_selector)
                data['stock'] = stock_element.text.strip()
            except Exception:
                self.logger.warning("Stock element not found")

        # Descripción
        description_selector = category.selectors.get('description_selector')
        if description_selector:
            try:
                description_element = self.driver.find_element(By.XPATH, description_selector)
                data['description'] = description_element.text.strip()
            except Exception:
                self.logger.warning("Description element not found")

        # Idioma desde descripción
        language_selector = category.selectors.get('language_selector')
        if language_selector and 'description' in data:
            try:
                pattern = r"Idioma:\s*([^\n\.]+)\."
                match = re.search(pattern, data['description'])
                data['language'] = match.group(1) if match else 'unknown'
            except Exception:
                self.logger.warning("Error extracting language")
                data['language'] = "unknown"

        # Imagen
        image_xpath = category.selectors.get('image_selector')
        try:
            if image_xpath:
                img_el = self.driver.find_element(By.XPATH, image_xpath)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", img_el)
                time.sleep(1.5)

                img_url = img_el.get_attribute("data-src") or img_el.get_attribute("src")
                if not img_url or img_url.startswith("data:image"):
                    self.logger.warning("Image fallback failed: placeholder found")
                    img_url = self.url_to_image.get(product_url, "")

                data["img_url"] = img_url
            else:
                data["img_url"] = self.url_to_image.get(product_url, "")
        except Exception as e:
            self.logger.warning(f"Image element not found: {e}")
            data["img_url"] = self.url_to_image.get(product_url, "")

        return data
