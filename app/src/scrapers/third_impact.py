import time
import re
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class ThirdImpact(BaseScraper):
    
    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url,wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')

        if not urls_selector:
            return []

        if urls_selector.startswith('//'):
            elements = self.find_elements(soup, urls_selector, 'xpath')
        else:
            elements = self.find_elements(soup, urls_selector, 'css')

        if not elements:
            return []

        product_urls = []
        for element in elements:
            try:
                title = self.get_text(element)
                url = self.get_attribute(element, 'href')

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
                    data['price'] = match.group() if match else price_text
                else:
                    data['price'] = ""
            except Exception:
                data['price'] = ""

        
        try:
            img_element = soup.select_one("picture img")
            if img_element:
                img_url = img_element.get('data-src') or img_element.get('src')
                if img_url and not img_url.startswith("data:image"):
                    if img_url.startswith('/'):
                        base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                        img_url = base_url + img_url
                    data["img_url"] = img_url
                else:
                    self.logger.warning("Image fallback failed: placeholder found")
                    data["img_url"] = ""
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"Image element not found: {e}")
            data["img_url"] = ""

        
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
                pass

        language_selector = category.selectors.get('language_selector')
        if language_selector:
            try:
                if language_selector.startswith('//'):
                    language_elements = self.find_elements(soup, language_selector, 'xpath')
                else:
                    language_elements = self.find_elements(soup, language_selector, 'css')
                
                if language_elements:
                    
                    first_lang = self.get_text(language_elements[0])
                    data['language'] = first_lang if first_lang else "unknown"
                    
                    
                    data['stock'] = len(language_elements) > 0
                else:
                    data['language'] = "Español"  
                    data['stock'] = True
            except Exception:
                data['language'] = "unknown"
                data['stock'] = False

        return data