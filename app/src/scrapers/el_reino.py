import time
import re
import traceback
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class ElReinoScraper(BaseScraper):
    
    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url,wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        containers = soup.select("div.product-element-bottom")
        urls = []

        for container in containers:
            try:
                a_tag = container.select_one("a[href*='/producto/']")
                if a_tag:
                    url = a_tag.get('href', '')
                    name = a_tag.get_text(strip=True)

                    if name and url:
                        if url.startswith('/'):
                            base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                            url = base_url + url
                        urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error extracting URL or name: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        
        try:
            soup = self.get_page(product_url)
        except Exception as e:
            self.logger.error(f"Failed to load product page {product_url}: {e}")
            return {}

        data = {}

        try:
            title_element = soup.select_one("h1")
            if title_element:
                data["name"] = title_element.get_text(strip=True)
            else:
                data["name"] = "undefined"
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        try:
            alternative_price = self.extract_price(soup)
            data["price"] = alternative_price if alternative_price else ""
        except Exception as e:
            traceback.print_exc()
            self.logger.warning(f"Price not found: {e}")
            data["price"] = ""

        image_selector = category.selectors.get("image_selector")
        try:
            if image_selector:
                if image_selector.startswith('//'):
                    image_el = self.find_element(soup, image_selector, 'xpath')
                else:
                    image_el = self.find_element(soup, image_selector, 'css')
                
                if image_el:
                    img_url = self.get_attribute(image_el, "src")
                    if img_url and not img_url.startswith("data:image"):
                        if img_url.startswith('/'):
                            base_url = product_url.split('/')[0] + '//' + product_url.split('/')[2]
                            img_url = base_url + img_url
                        data["img_url"] = img_url
                    else:
                        data["img_url"] = ""
                        self.logger.warning("Fallback image or empty URL encountered")
                else:
                    data["img_url"] = ""
            else:
                data["img_url"] = ""
        except Exception as e:
            self.logger.warning(f"Image not found: {e}")
            data["img_url"] = ""

        return data

    def extract_price(self, soup: BeautifulSoup) -> str:
        price_elements = soup.select("p.price span")
        
        if not price_elements:
            self.logger.warning("Price element not found")
            return ""

        if len(price_elements) == 1:
            text = price_elements[0].get_text(strip=True)
            match = re.search(r'[\d.,]+', text)
            if match:
                matched_text = match.group(0)
                return matched_text
            else:
                self.logger.warning("No valid price found in the text")
                return ""
        else:
            for span in price_elements:
                span_text = span.get_text(strip=True)
                if 'actual' in span_text.lower():
                    match = re.search(r'[\d.,]+', span_text)
                    if match:
                        matched_text = match.group(0)
                        return matched_text
            
            for span in price_elements:
                span_text = span.get_text(strip=True)
                match = re.search(r'[\d.,]+', span_text)
                if match:
                    matched_text = match.group(0)
                    return matched_text
        
        return ""
