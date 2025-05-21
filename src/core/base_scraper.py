import os
import json
import datetime
import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from src.core.category import Category
from src.core.logger_factory import LoggerFactory
from src.core.webdriver_factory import WebDriverFactory
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BaseScraper(ABC):
    
    def __init__(self, name: str, config: Dict[str, Any]):

        self.name = name
        self.config = config
        self.logger = LoggerFactory.create_logger(f"scraper.{name}")
        self.driver = None
        self.results = {}  
        self.categories = self._initialize_categories(config.get('categories', {}))
        self.batch_size = None
    
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
            headless = self.config.get('headless', True)
            user_agent = self.config.get('user_agent')
            window_size = self.config.get('window_size', "1920,1080")
            self.batch_size = self.config.get('batch_size', 10)
            
            self.driver = WebDriverFactory.create_chrome_driver(
                headless=headless,
                user_agent=user_agent,
                window_size=window_size
            )
        except Exception as e:
            self.logger.error(f"Failed to set up WebDriver: {e}", exc_info=True)
            raise
    
    def teardown(self) -> None:
        if self.driver:
            self.logger.info("Closing WebDriver")
            self.driver.quit()
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:

        if not self.driver:
            self.logger.warning("Cannot take screenshot: WebDriver not initialized")
            return ""
        
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        if not filename:
            filename = f"screenshots/{self.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        elif not filename.startswith('screenshots/'):
            filename = f"screenshots/{filename}"
        
        self.driver.save_screenshot(filename)
        self.logger.info(f"Screenshot saved to {filename}")
        return filename
    
    def wait_for_element(self, selector: str, by: str = By.XPATH, timeout: int = 10) -> bool:

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element {selector}")
            return False
    
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
        
        if not filename:
            filename = f"data/{base_filename}"
        elif not filename.startswith('data/'):
            filename = f"data/{filename}"
        
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
            
            for category in self.categories:
                self.logger.info(f"Processing category: {category.name}")
                
                self.results[category.name] = []
                
                self.navigate_to_category(category)
                
                product_urls = self.extract_product_urls(category)
                self.logger.info(f"Found {len(product_urls)} product URLs in category {category.name}")
                if len(product_urls) > self.batch_size:
                    self.logger.info(f"Limiting to the first {self.batch_size} products")
                    product_urls = product_urls[:self.batch_size]
                
                for idx, (product_name, product_url) in enumerate(product_urls):
                    self.logger.info(f"Processing product {idx+1}/{len(product_urls)}: {product_name}")
                    product_data = self.process_product(product_url, category)
                    
                    if product_data:
                        product_data['name'] = product_name
                        product_data['url'] = product_url
                        product_data['category'] = category.name
                        self.results[category.name].append(product_data)
            
            self.logger.info(f"Scraping completed. Found items in {len(self.results)} categories.")
            return self.results
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}", exc_info=True)
            return {}
        finally:
            self.teardown()
    
    @abstractmethod
    def navigate_to_category(self, category: Category) -> None:

        pass
    
    @abstractmethod
    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:

        pass
    
    @abstractmethod
    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:

        pass

