import time
import re
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class HunterCardTCG(BaseScraper):

    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url, wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')

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

                if url and not title:
                    title = url.split('/')[-1].replace('-', ' ').capitalize()

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

        try:
            name_element = soup.select_one("h1.product_title")
            if name_element:
                data["name"] = name_element.get_text(strip=True)
            else:
                self.logger.warning("Name element not found")
                data["name"] = "unknown"
        except Exception:
            self.logger.warning("Name element not found")
            data["name"] = "unknown"

        try:
            price_selector = category.selectors.get('price_selector')
            if price_selector:
                if price_selector.startswith('//'):
                    price_element = self.find_element(soup, price_selector, 'xpath')
                else:
                    price_element = self.find_element(soup, price_selector, 'css')

                if price_element:
                    price_text = self.get_text(price_element)
                    pattern = r'\d+(?:[.,]\d+)?'
                    match = re.search(pattern, price_text.replace('.', '').replace(',', '.'))
                    data["price"] = match.group() if match else "unknown"
                else:
                    data["price"] = "unknown"
            else:
                data["price"] = "unknown"
        except Exception:
            self.logger.warning("Price element not found")
            data["price"] = "unknown"

        try:
            stock_selector = category.selectors.get("stock_selector")
            if stock_selector:
                if stock_selector.startswith('//'):
                    stock_element = self.find_element(soup, stock_selector, 'xpath')
                else:
                    stock_element = self.find_element(soup, stock_selector, 'css')

                if stock_element:
                    data["stock"] = self.get_text(stock_element)
        except Exception:
            pass

        try:
            desc_selector = category.selectors.get("description_selector")
            if desc_selector:
                if desc_selector.startswith('//'):
                    desc_element = self.find_element(soup, desc_selector, 'xpath')
                else:
                    desc_element = self.find_element(soup, desc_selector, 'css')

                if desc_element:
                    data["description"] = self.get_text(desc_element)
        except Exception:
            pass

        try:
            lang_selector = category.selectors.get("language_selector")
            if lang_selector:
                if lang_selector.startswith('//'):
                    lang_element = self.find_element(soup, lang_selector, 'xpath')
                else:
                    lang_element = self.find_element(soup, lang_selector, 'css')

                if lang_element:
                    lang_text = self.get_text(lang_element)
                    pattern = r"[–-]\s*([^\s\n]+)"
                    matches = re.findall(pattern, lang_text)
                    data['language'] = matches[-1] if matches else "unknown"
                else:
                    data["language"] = "unknown"
            else:
                data["language"] = "unknown"
        except Exception:
            data["language"] = "unknown"

        image_selector = category.selectors.get("image_selector")
        try:
            if image_selector:
                if image_selector.startswith('//'):
                    image_el = self.find_element(soup, image_selector, 'xpath')
                else:
                    image_el = self.find_element(soup, image_selector, 'css')

                if image_el:
                    img_url = self.get_attribute(image_el, "src")
                    if img_url and img_url.startswith('/'):
                        base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                        img_url = base_url + img_url
                    data["img_url"] = img_url
                else:
                    data["img_url"] = ""
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"Image not found: {e}")
            data["img_url"] = ""

        return data
