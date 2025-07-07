import time
import re
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class GuildDreamsScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_to_image: Dict[str, str] = {}

    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url, wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')
        image_selector = category.selectors.get('image_selector')

        if not urls_selector:
            self.logger.error(f"No urls_selector defined for category {category.name}")
            return []

        if urls_selector.startswith('//'):
            elements = self.find_elements(soup, urls_selector, 'xpath')
        else:
            elements = self.find_elements(soup, urls_selector, 'css')

        if not elements:
            self.logger.error(f"Couldn't find title elements for category {category.name}")
            return []

        self.logger.info(f"Found {len(elements)} title elements")

        product_urls = []
        for element in elements:
            try:
                title = self.get_text(element)
                url = self.get_attribute(element, 'href')

                try:
                    container = element.find_parent(class_='bs-product') or element.find_parent('div')
                    if container:
                        img_el = container.find('img')
                        if img_el:
                            img_url = img_el.get('data-src') or img_el.get('src')
                            if img_url and not img_url.startswith("data:image"):
                                if img_url.startswith('/'):
                                    base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                                    img_url = base_url + img_url
                                self.url_to_image[url] = img_url
                            else:
                                self.url_to_image[url] = ""
                        else:
                            self.url_to_image[url] = ""
                    else:
                        self.url_to_image[url] = ""
                except Exception:
                    self.url_to_image[url] = ""

                if title and url:
                    if url.startswith('/'):
                        base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                        url = base_url + url
                    product_urls.append((title, url))
            except Exception as e:
                self.logger.warning(f"Error extracting element data: {e}")

        return product_urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")

        try:
            soup = self.get_page(product_url)
        except Exception as e:
            self.logger.error(f"Failed to load product page {product_url}: {e}")
            return {}

        data = {}

        title_selector = category.selectors.get('title_selector')
        try:
            if title_selector:
                if title_selector.startswith('//'):
                    title_element = self.find_element(soup, title_selector, 'xpath')
                else:
                    title_element = self.find_element(soup, title_selector, 'css')

                if title_element:
                    data['name'] = self.get_text(title_element)
                else:
                    self.logger.warning("Title element not found")
                    data['name'] = "unknown"
            else:
                self.logger.warning("Title selector not defined")
                data['name'] = "unknown"
        except Exception:
            self.logger.warning("Name element not found")
            data['name'] = "unknown"

        price_selector = category.selectors.get('price_selector')
        try:
            if price_selector:
                if price_selector.startswith('//'):
                    price_element = self.find_element(soup, price_selector, 'xpath')
                else:
                    price_element = self.find_element(soup, price_selector, 'css')

                if price_element:
                    price_text = self.get_text(price_element)
                    pattern = r'\b\d+(?:[.,]\d{3})*(?:[.,]\d{2})?\b'
                    match = re.search(pattern, price_text.replace('.', '').replace(',', '.'))
                    data['price'] = match.group() if match else price_text
                else:
                    self.logger.warning("Price element not found")
                    data['price'] = "unknown"
            else:
                self.logger.warning("Price selector not defined")
                data['price'] = "unknown"
        except Exception:
            self.logger.warning("Price element not found")
            data['price'] = "unknown"

        stock_selector = category.selectors.get('stock_selector')
        if stock_selector:
            try:
                if stock_selector.startswith('//'):
                    stock_element = self.find_element(soup, stock_selector, 'xpath')
                else:
                    stock_element = self.find_element(soup, stock_selector, 'css')

                if stock_element:
                    data['stock'] = self.get_text(stock_element)
            except Exception:
                self.logger.warning("Stock element not found")

        description_selector = category.selectors.get('description_selector')
        if description_selector:
            try:
                if description_selector.startswith('//'):
                    description_element = self.find_element(soup, description_selector, 'xpath')
                else:
                    description_element = self.find_element(soup, description_selector, 'css')

                if description_element:
                    data['description'] = self.get_text(description_element)
            except Exception:
                self.logger.warning("Description element not found")

        language_selector = category.selectors.get('language_selector')
        if language_selector and 'description' in data:
            try:
                pattern = r"Idioma:\s*([^\n\.]+)\."
                match = re.search(pattern, data['description'])
                data['language'] = match.group(1) if match else 'unknown'
            except Exception:
                self.logger.warning("Error extracting language")
                data['language'] = "unknown"

        image_xpath = category.selectors.get('image_selector')
        try:
            img_url = ""
            if image_xpath:
                if image_xpath.startswith('//'):
                    img_el = self.find_element(soup, image_xpath, 'xpath')
                else:
                    img_el = self.find_element(soup, image_xpath, 'css')

                if img_el:
                    img_url = img_el.get('data-src') or img_el.get('src')
                    if img_url and not img_url.startswith("data:image"):
                        if img_url.startswith('/'):
                            base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                            img_url = base_url + img_url
                    else:
                        self.logger.warning("Image fallback failed: placeholder found")
                        img_url = self.url_to_image.get(product_url, "")
                else:
                    img_url = self.url_to_image.get(product_url, "")
            else:
                img_url = self.url_to_image.get(product_url, "")

            data["img_url"] = img_url
        except Exception as e:
            self.logger.warning(f"Image element not found: {e}")
            data["img_url"] = self.url_to_image.get(product_url, "")

        return data
