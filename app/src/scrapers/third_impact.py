import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


class ThirdImpact(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:

        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')

        if not self.wait_for_element(urls_selector):
            return []

        self.take_screenshot(f"{self.name}_{category.name}_listing.png")

        elements = self.driver.find_elements(By.XPATH, urls_selector)

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

        price_selector = category.selectors.get('price_selector')
        if price_selector:
            price_element = self.driver.find_element(By.XPATH, price_selector)
            price_text = price_element.text.strip()
            pattern = r'\b\d+(?:\.\d+)?\b'
            match = re.search(pattern, price_text)
            if match:
                data['price'] = match.group()
            else:
                data['price'] = price_text
                # Imagen
        try:
            img_element = self.driver.find_element(By.XPATH, "//picture//img")
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", img_element)
            time.sleep(1)

            img_url = img_element.get_attribute(
                "data-src") or img_element.get_attribute("src")
            if not img_url or img_url.startswith("data:image"):
                self.logger.warning("Image fallback failed: placeholder found")
                img_url = ""

            data["img_url"] = img_url
        except Exception as e:
            self.logger.warning(f"Image element not found: {e}")
            data["img_url"] = ""

        description_selector = category.selectors.get('description_selector')
        if description_selector:
            description_element = self.driver.find_element(
                By.XPATH, description_selector)
            data['description'] = description_element.text.strip()

        language_selector = category.selectors.get('language_selector')
        if language_selector:
            language_elements = self.driver.find_elements(By.XPATH, language_selector)
            for language in language_elements:
                text = language.text.strip()
                data['language'] = self.process_language_text(text)
            data['stock'] = self.get_stock_data(language_elements)
        return data

    def process_language_text(self, text: str) -> str:
        if text:
            text = text.strip()
            return text
        else:
            return "unknown"

    def get_stock_data(self, language_elements: List[WebElement]) -> Dict[str, bool]:
        stock_by_language = {}
        if len(language_elements) == 0:
            default_language_stock = self.get_stock_for_default_language()
            stock_by_language["Español"] = default_language_stock
            return stock_by_language

        for language in language_elements:
            text = language.text.strip()
            if text:
                stock_by_language[text] = self.get_stock_by_border_style(language)
            else:
                stock_by_language["unknown"] = False
        return stock_by_language

    def get_stock_for_default_language(self) -> str:
        wait = WebDriverWait(self.driver, 10)
        stock_elements = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//table/tbody/tr/td[2]")))
        for stock in stock_elements:
            text = stock.text.strip()

            if text != "Agotado":
                return True
        return False

    def get_stock_by_border_style(self, element: WebElement) -> bool:
        border_style = element.value_of_css_property("border-style")
        if border_style != "dashed":
            return True
        else:
            return False
