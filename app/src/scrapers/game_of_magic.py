import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import urllib.parse


class GameOfMagicScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:

        try:
            containers_selector = category.selectors.get('product_selector')
            urls_selector = category.selectors.get('urls_selector')

            if not containers_selector or not urls_selector:
                raise ValueError("Missing required selectors in config")

            page_source = self.driver.page_source

            soup = BeautifulSoup(page_source, 'html.parser')

            containers = soup.select(containers_selector)
            self.logger.info(f"Found {len(containers)} product containers")

            urls = []
            for container in containers:
                try:
                    a_tag = container.select_one(urls_selector)

                    if not a_tag:
                        continue

                    url = a_tag.get("href")
                    name = a_tag.get("title") or a_tag.get_text(strip=True)

                    if url and name:
                        if url.startswith('/'):
                            base_url = self._get_base_url()
                            url = urllib.parse.urljoin(base_url, url)

                        urls.append((name.strip(), url.strip()))

                except Exception as e:
                    self.logger.warning(f"Error processing product container: {e}")

            return urls

        except Exception as e:
            self.logger.error(f"Error extracting product URLs: {e}")
            return []

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

    def _get_base_url(self) -> str:
        try:
            if hasattr(self, 'driver') and self.driver:
                current_url = self.driver.current_url
                parsed = urllib.parse.urlparse(current_url)
                return f"{parsed.scheme}://{parsed.netloc}"
            return ''
        except Exception:
            return ''
