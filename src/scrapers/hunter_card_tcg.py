import time
import re
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class HunterCardTCG(BaseScraper):
    def navigate_to_category(self,category: Category) -> None:

        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))
    
    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        urls_selector = category.selectors.get('urls_selector')
        
        if not self.wait_for_element(urls_selector):
            self.logger.error(f"Couldn't find title elements for category {category.name}")
            return []
        
        self.take_screenshot(f"{self.name}_{category.name}_listing.png")
        
        elements = self.driver.find_elements(By.XPATH, urls_selector)
        self.logger.info(f"Found {len(elements)} title elements")
        
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
    
    def process_product(self,product_url: str, category: Category) -> Dict[str, Any]:
        self.logger.info(f"Processing product: {product_url}")
        self.driver.get(product_url)
        
        time.sleep(self.config.get('page_load_delay', 2))
        

        data = {}
            

        price_selector = category.selectors.get('price_selector')
        if price_selector:
            price_element = self.driver.find_element(By.XPATH, price_selector)
            price_text= price_element.text.strip()
            pattern = r'\b\d+(?:\.\d+)?\b'
            match = re.search(pattern, price_text)
            if match:
                data['price'] = match.group()
            else:
                self.logger.warning(f"Price not found in text: {price_text}")
                data['price'] = price_text

        

        stock_selector = category.selectors.get('stock_selector')
        if stock_selector:
            stock_element = self.driver.find_element(By.XPATH, stock_selector)
            data['stock'] = stock_element.text.strip()
        
        description_selector = category.selectors.get('description_selector')
        if description_selector:
            description_element = self.driver.find_element(By.XPATH, description_selector)
            data['description'] = description_element.text.strip()

        language_selector = category.selectors.get('language_selector')
        language_element = self.driver.find_element(By.XPATH, language_selector)

        if language_selector:
            pattern = r"[–-]\s*([^\s\n]+)"
            matches = re.findall(pattern, language_element.text)
            if match:
                data['language'] = matches[-1]
            else:
                self.self.logger.warning(f"Language not found in text: {description_element.text}")
                data['language'] = 'unknown'
        
        return data
    
   