import os
import json
import datetime
import re
import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from src.core.category import Category
from src.core.logger_factory import LoggerFactory
from src.utils.css_contain_adapter import EnhancedSelector, StockChecker
from src.utils.session import SimpleReliableSession
from src.utils.session_html import RequestsHTMLSession
from bs4 import BeautifulSoup
import urllib.parse


class BaseScraper(ABC):

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = LoggerFactory.create_logger(f"scraper.{name}")
        self.session = None
        self.results = {}
        self.categories = self._initialize_categories(config.get('categories', {}))
        self.batch_size = None
        self.report = {}

    def _initialize_categories(self, categories_config: Dict[str, Any]) -> List[Category]:
        categories = []
        for category_name, category_config in categories_config.items():
            url = category_config.get('url')
            selectors = category_config.get('selectors', {})

            if url:
                categories.append(Category(category_name, url, selectors))
                self.logger.info(f"Initialized category: {category_name}")
            else:
                self.logger.warning(f"Skipping category {category_name}: No URL provided")

        return categories

    def setup(self) -> None:
        try:
            self.logger.info(f"Setting up {self.name} scraper")
            self.batch_size = self.config.get('batch_size', 4)
            
            self.session = RequestsHTMLSession()
            
            self.logger.info("SimpleReliableSession configured")
            
        except Exception as e:
            self.logger.error(f"Failed to set up session: {e}", exc_info=True)
            raise

    def teardown(self) -> None:
        if self.session:
            self.logger.info("Closing session")
            self.session.close()

    def get_page(self, url: str,wait_for=None) -> BeautifulSoup:
        try:
            self.logger.info(f"Fetching URL: {url}")
            soup = self.session.get(url,wait_for=wait_for)
            return soup
            
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            raise

    def find_elements(self, soup: BeautifulSoup, selector: str, selector_type: str = 'css') -> List:
        try:
            if selector_type == 'xpath':
                css_selector = self._xpath_to_css(selector)
                elements = EnhancedSelector.select(soup, css_selector)
            else:
                elements = EnhancedSelector.select(soup, selector)
            
            return elements
        except Exception as e:
            self.logger.warning(f"Error finding elements with selector {selector}: {e}")
            return []

    def find_element(self, soup: BeautifulSoup, selector: str, selector_type: str = 'css'):
        elements = self.find_elements(soup, selector, selector_type)
        return elements[0] if elements else None

    def check_stock(self, soup: BeautifulSoup, stock_selector: str = None) -> str:
        try:
            if StockChecker.is_out_of_stock(soup, stock_selector):
                return "out_of_stock"
            else:
                return "in_stock"
        except Exception as e:
            self.logger.warning(f"Error checking stock: {e}")
            return "unknown"

    def get_text(self, element) -> str:
        if element:
            text = element.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        return ""

    def get_attribute(self, element, attribute: str) -> str:
        if element and hasattr(element, 'get'):
            return element.get(attribute, '')
        return ""

    def _xpath_to_css(self, xpath: str) -> str:
        if not xpath.startswith('//'):
            return xpath
        
        conversions = [
            (r'^//', ''),
            (r'/(\w+)', r' > \1'),
            (r"contains\(@class,\s*['\"]([^'\"]+)['\"]\)", r'[class*="\1"]'),
            (r"contains\(@href,\s*['\"]([^'\"]+)['\"]\)", r'[href*="\1"]'),
            (r"@class\s*=\s*['\"]([^'\"]+)['\"]", r'.\1'),
            (r"@id\s*=\s*['\"]([^'\"]+)['\"]", r'#\1'),
            (r'\[(\d+)\]', r':nth-child(\1)'),
            (r'\s+', ' '),
        ]
        
        css = xpath
        for pattern, replacement in conversions:
            css = re.sub(pattern, replacement, css)
        
        return css.strip() if css.strip() else '*'

    def save_screenshot(self, soup: BeautifulSoup, filename: Optional[str] = None) -> str:
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')

        if not filename:
            filename = f"screenshots/{self.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        elif not filename.startswith('screenshots/'):
            filename = f"screenshots/{filename}"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            self.logger.info(f"HTML saved to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save HTML: {e}")
            return ""

    def save_results(self, category_name: Optional[str] = None, filename: Optional[str] = None, format: str = 'json') -> str:
        if category_name and category_name in self.results:
            results_to_save = self.results[category_name]
        elif not category_name:
            results_to_save = []
            for cat_results in self.results.values():
                results_to_save.extend(cat_results)
        else:
            self.logger.warning(f"No results found for category: {category_name}")
            return ""

        if not results_to_save:
            self.logger.warning("No results to save")
            return ""

        if not os.path.exists('data'):
            os.makedirs('data')

        base_filename = f"{self.name}_{category_name if category_name else 'all'}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs('data', exist_ok=True)
        if category_name:
            os.makedirs(f"data/{category_name}", exist_ok=True)
        
        if not filename:
            if category_name:
                filename = f"data/{category_name}/{base_filename}"
            else:
                filename = f"data/{base_filename}"
        elif not filename.startswith('data/'):
            if category_name:
                filename = f"data/{category_name}/{base_filename}"
            else:
                filename = f"data/{base_filename}"

        try:
            if format.lower() == 'csv':
                full_filename = f"{filename}.csv"
                df = pd.DataFrame(results_to_save)
                df.to_csv(full_filename, index=False)
            elif format.lower() == 'json':
                full_filename = f"{filename}.json"
                with open(full_filename, 'w', encoding='utf-8') as f:
                    json.dump(results_to_save, f, ensure_ascii=False, indent=4)
            else:
                self.logger.error(f"Unsupported format: {format}")
                return ""

            self.logger.info(f"Results saved to {full_filename}")
            return full_filename
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}", exc_info=True)
            return ""

    def run(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            self.setup()
            self.logger.info(f"Starting {self.name} scraper")

            process_report = {}
            for category in self.categories:
                self.logger.info(f"Processing category: {category.name}")

                self.results[category.name] = []
                soup = self.navigate_to_category(category)

                product_urls = self.extract_product_urls(soup, category)

                self.logger.info(f"Found {len(product_urls)} product URLs in category {category.name}")
                if len(product_urls) > self.batch_size:
                    self.logger.info(f"Limiting to the first {self.batch_size} products")
                    product_urls = product_urls[:self.batch_size]
                
                product_count = len(product_urls)
                processed_count = 0
                
                for idx, (product_name, product_url) in enumerate(product_urls):
                    self.logger.info(f"Processing product {idx+1}/{len(product_urls)}: {product_name}")
                    product_data = self.process_product(product_url, category)

                    if product_data:
                        product_data['name'] = product_name
                        product_data['url'] = product_url
                        product_data['game'] = category.name
                        product_data['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        product_data['store'] = self.name
                        product_data['product_type'] = self.detect_type(product_name)
                        price = self.clean_price(product_data.get('price', 0))
                        product_data['price'] = price
                        product_data['min_price'] = price
                        if len(product_data.get('description', "")) > 500:
                            self.logger.info(f"Truncating description for {product_name}")
                            product_data['description'] = product_data['description'][:450] + "..."
                        processed_count += 1
                        self.results[category.name].append(product_data)
                
                process_report[category.name] = {
                    'total_products': product_count,
                    'processed_products': processed_count,
                    'success_rate': (processed_count / product_count) * 100 if product_count > 0 else 0
                }
            
            self.report = process_report
            self.logger.info(f"Scraping completed. Found items in {len(self.results)} categories.")
            return self.results
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}", exc_info=True)
            return {}
        finally:
            self.teardown()

    def get_report(self) -> Dict[str, Any]:
        return self.report

    def detect_type(self, product_name: str) -> str:
        name = product_name.lower()
        if "booster" in name:
            return "booster"
        if "bundle" in name:
            return "bundle"
        else:
            return "singles"

    def clean_price(self, raw_price):
        if not raw_price:
            return 0
        match = re.findall(r'\d+', str(raw_price))
        if not match:
            return 0
        return int(''.join(match))

    @abstractmethod
    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        pass

    @abstractmethod
    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:
        pass

    @abstractmethod
    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        pass
