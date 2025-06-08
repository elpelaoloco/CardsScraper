import time
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
        containers_xpath = category.selectors.get('product_selector')
        self.wait_for_element(containers_xpath)

        containers = self.driver.find_elements(By.XPATH, containers_xpath)
        self.logger.info(f"Found {len(containers)} product containers")
        urls = []

        for container in containers:
            try:
                # URL y nombre del producto desde el <a>
                a_tag = container.find_element(By.XPATH, category.selectors['urls_selector'])
                url = a_tag.get_attribute("href")
                name = a_tag.get_attribute("title") or a_tag.text.strip()

                if not name or not url:
                    continue

                urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error processing product container: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}

        # Extraer nombre desde el h1
        try:
            title_xpath = category.selectors.get('title_selector')
            if title_xpath:
                name_el = self.driver.find_element(By.XPATH, title_xpath)
                data["name"] = name_el.text.strip()
            else:
                data["name"] = "undefined"
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        # Extraer precio
        price_xpath = category.selectors.get('price_selector')
        try:
            price_el = self.driver.find_element(By.XPATH, price_xpath)
            price_text = price_el.text.strip()
            data["price"] = price_text if price_text else ""
        except Exception as e:
            self.logger.warning(f"No price found: {e}")
            data["price"] = ""

        return data
