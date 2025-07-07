import time
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class GameOfMagicScraper(BaseScraper):

    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url, wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        containers_xpath = category.selectors.get('product_selector')

        if not containers_xpath:
            self.logger.error("No product_selector defined in config")
            return []

        if containers_xpath.startswith('//'):
            containers = self.find_elements(soup, containers_xpath, 'xpath')
        else:
            containers = self.find_elements(soup, containers_xpath, 'css')

        self.logger.info(f"Found {len(containers)} product containers")
        urls = []

        for container in containers:
            try:
                urls_selector = category.selectors.get('urls_selector')
                if not urls_selector:
                    raise ValueError("No urls_selector defined in config")

                if urls_selector.startswith('//'):
                    relative_selector = urls_selector.replace('./', '').replace('//', '')
                    if 'a' in relative_selector:
                        a_tag = container.find('a')
                    else:
                        a_tag = container.select_one('a')
                else:
                    a_tag = container.select_one(urls_selector)

                if a_tag:
                    url = a_tag.get('href', '')
                    name = a_tag.get('title', '') or a_tag.get_text(strip=True)

                    if url and name:
                        if url.startswith('/'):
                            base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                            url = base_url + url
                        urls.append((name, url))
                else:
                    self.logger.warning("Product container doesn't contain a valid link")
            except Exception as e:
                self.logger.warning(f"Error processing product container: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")

        try:
            soup = self.get_page(product_url)
        except Exception as e:
            self.logger.error(f"Failed to load product page {product_url}: {e}")
            return {}

        data = {}

        title_xpath = category.selectors.get('title_selector')
        try:
            if title_xpath:
                if title_xpath.startswith('//'):
                    name_el = self.find_element(soup, title_xpath, 'xpath')
                else:
                    name_el = self.find_element(soup, title_xpath, 'css')

                if name_el:
                    data["name"] = self.get_text(name_el)
                else:
                    data["name"] = "undefined"
            else:
                data["name"] = "undefined"
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        price_xpath = category.selectors.get('price_selector')
        try:
            if price_xpath:
                if price_xpath.startswith('//'):
                    price_el = self.find_element(soup, price_xpath, 'xpath')
                else:
                    price_el = self.find_element(soup, price_xpath, 'css')

                if price_el:
                    price_text = self.get_text(price_el)
                    data["price"] = price_text if price_text else ""
                else:
                    data["price"] = ""
            else:
                data["price"] = ""
        except Exception as e:
            self.logger.warning(f"No price found: {e}")
            data["price"] = ""

        image_xpath = category.selectors.get('image_selector')
        try:
            if image_xpath:
                if image_xpath.startswith('//'):
                    img_el = self.find_element(soup, image_xpath, 'xpath')
                else:
                    img_el = self.find_element(soup, image_xpath, 'css')

                if img_el:
                    img_url = self.get_attribute(img_el, "src")
                    if img_url and img_url.startswith('/'):
                        base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                        img_url = base_url + img_url
                    data["img_url"] = img_url
                else:
                    data["img_url"] = ""
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"No image found: {e}")
            data["img_url"] = ""

        return data
