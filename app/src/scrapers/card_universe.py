import time
import re
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class CardUniverseScraper(BaseScraper):
    
    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url,wait_for=wait_for)
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
                title_text = self.get_text(element)
                title_name = title_text.split('\n')[0].strip() if title_text else ""
                url = self.get_attribute(element, 'href')

                if title_name and url:
                    if url.startswith('/'):
                        base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                        url = base_url + url
                    product_urls.append((title_name, url))
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

        price_selector = category.selectors.get('price_selector')
        if price_selector:
            try:
                if price_selector.startswith('//'):
                    price_element = self.find_element(soup, price_selector, 'xpath')
                else:
                    price_element = self.find_element(soup, price_selector, 'css')
                
                if price_element:
                    price_text = self.get_text(price_element)
                    pattern = r'\b\d+(?:\.\d+)?\b'
                    match = re.search(pattern, price_text)
                    if match:
                        data['price'] = match.group()
                    else:
                        self.logger.warning(f"Price not found in text: {price_text}")
                        data['price'] = price_text
                else:
                    self.logger.warning("Price element not found")
                    data['price'] = ""
            except Exception as e:
                self.logger.warning(f"Error extracting price: {e}")
                data['price'] = ""

        language_selector = category.selectors.get('language_selector')
        if language_selector:
            try:
                if language_selector.startswith('//'):
                    language_elements = self.find_elements(soup, language_selector, 'xpath')
                else:
                    language_elements = self.find_elements(soup, language_selector, 'css')
                
                languages = []
                for option in language_elements:
                    lang_text = self.get_text(option)
                    if lang_text:
                        languages.append(lang_text)
                data['language'] = ', '.join(languages)
            except Exception as e:
                self.logger.warning(f"Error extracting languages: {e}")
                data['language'] = ""

        data['stock'] = 'unknown'

        description_selector = category.selectors.get('description_selector')
        if description_selector:
            try:
                if description_selector.startswith('//'):
                    description_element = self.find_element(soup, description_selector, 'xpath')
                else:
                    description_element = self.find_element(soup, description_selector, 'css')
                
                if description_element:
                    data['description'] = self.get_text(description_element)
                else:
                    data['description'] = ""
            except Exception as e:
                self.logger.warning(f"Error extracting description: {e}")
                data['description'] = ""

        try:
            img_selectors = [
                "div[id^='ImageZoom-template'] img",
                ".product-single__photo img",
                ".product__photo img",
                "img[src*='product']"
            ]
            
            img_url = ""
            for selector in img_selectors:
                img_element = self.find_element(soup, selector, 'css')
                if img_element:
                    img_url = self.get_attribute(img_element, 'src')
                    if img_url:
                        break
            
            if img_url and img_url.startswith('/'):
                base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                img_url = base_url + img_url
                
            data["img_url"] = img_url
        except Exception as e:
            self.logger.warning(f"Error extracting image: {e}")
            data["img_url"] = ""

        return data
