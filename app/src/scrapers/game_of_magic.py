import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


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
                urls_selector = category.selectors.get('urls_selector')
                if not urls_selector:
                    raise ValueError("No urls_selector defined in config")

                a_tag = container.find_element(By.XPATH, urls_selector)
                url = a_tag.get_attribute("href")
                name = a_tag.get_attribute("title") or a_tag.text.strip()

                if url and name:
                    urls.append((name, url))
            except NoSuchElementException:
                self.logger.warning("Product container doesn't contain a valid link")
            except Exception as e:
                self.logger.warning(f"Error processing product container: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}

        # Título
        title_xpath = category.selectors.get('title_selector')
        try:
            if title_xpath:
                name_el = self.driver.find_element(By.XPATH, title_xpath)
                data["name"] = name_el.text.strip()
            else:
                data["name"] = "undefined"
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        # Precio
        price_xpath = category.selectors.get('price_selector')
        try:
            if price_xpath:
                price_el = self.driver.find_element(By.XPATH, price_xpath)
                price_text = price_el.text.strip()
                data["price"] = price_text if price_text else ""
            else:
                data["price"] = ""
        except Exception as e:
            self.logger.warning(f"No price found: {e}")
            data["price"] = ""

        # Imagen
        image_xpath = category.selectors.get('image_selector')
        try:
            if image_xpath:
                img_el = self.driver.find_element(By.XPATH, image_xpath)
                data["img_url"] = img_el.get_attribute("src")
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"No image found: {e}")
            data["img_url"] = ""

        return data
