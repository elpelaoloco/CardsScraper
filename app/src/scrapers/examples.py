
from selenium.webdriver.common.by import By
from typing import List, Dict, Any, Tuple
from core.category import Category
from core.base_scraper import BaseScraper
import time
import datetime

class HackerNewsScraper(BaseScraper):
    """Scraper for Hacker News."""
    
    def navigate_to_category(self, category: Category) -> None:
        """Navigate to a category (section) of Hacker News."""
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        
        time.sleep(self.config.get('page_load_delay', 2))
    
    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        """Extract article URLs from current Hacker News page."""
        title_selector = category.selectors.get('title_selector', '.titleline > a')
        
        if not self.wait_for_element(title_selector):
            self.logger.error(f"Couldn't find title elements for category {category.name}")
            return []
        

        self.take_screenshot(f"{self.name}_{category.name}_listing.png")
        

        elements = self.driver.find_elements(By.CSS_SELECTOR, title_selector)
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
    
    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        """
        Process a single article.
        
        Note: For Hacker News, we don't need to visit each article page
        since we have the main information already.
        """
        # In this case, we already captured the main data (title and URL)
        # in the extract_product_urls method, so we return an empty dict
        # that will be populated with name and URL in the run method
        return {}


class AmazonProductScraper(BaseScraper):
    """Scraper for Amazon product listings."""
    
    def navigate_to_category(self, category: Category) -> None:
        """Navigate to Amazon category page."""
        self.logger.info(f"Navigating to category {category.name}: {category.url}")
        self.driver.get(category.url)
        
        # Wait for page to load
        time.sleep(self.config.get('page_load_delay', 3))
    
    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        """Extract product URLs from Amazon category page."""
        product_selector = category.selectors.get('product_selector', '.s-result-item[data-component-type="s-search-result"]')
        title_selector = category.selectors.get('title_selector', 'h2 a span')
        link_selector = category.selectors.get('link_selector', 'h2 a')
        
        if not self.wait_for_element(product_selector):
            self.logger.error(f"Couldn't find product elements for category {category.name}")
            return []
        
        # Take screenshot for verification
        self.take_screenshot(f"{self.name}_{category.name}_listing.png")
        
        # Extract products
        products = self.driver.find_elements(By.CSS_SELECTOR, product_selector)
        self.logger.info(f"Found {len(products)} product elements")
        
        product_urls = []
        for product in products:
            try:
                # Find title element
                title_elements = product.find_elements(By.CSS_SELECTOR, title_selector)
                title = title_elements[0].text.strip() if title_elements else "Unknown Product"
                
                # Find URL element
                link_elements = product.find_elements(By.CSS_SELECTOR, link_selector)
                url = link_elements[0].get_attribute('href') if link_elements else None
                
                # Extract the actual product URL from the Amazon redirect URL
                if url and ('amazon.com' in url):
                    # Parse out the actual product page URL if needed
                    if '/dp/' in url:
                        url = url.split('/ref=')[0] if '/ref=' in url else url
                    
                    product_urls.append((title, url))
            except Exception as e:
                self.logger.warning(f"Error extracting product URL: {e}")
        
        return product_urls
    
    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        """Process a single Amazon product."""
        try:
            # Navigate to the product page
            self.logger.info(f"Navigating to product: {product_url}")
            self.driver.get(product_url)
            
            # Wait for page to load
            time.sleep(self.config.get('product_load_delay', 2))
            
            # Take screenshot
            self.take_screenshot(f"amazon_product_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            # Extract product details
            price_selector = category.selectors.get('price_selector', '#priceblock_ourprice, .a-price .a-offscreen')
            rating_selector = category.selectors.get('rating_selector', '.a-star-rating-wrapper, .a-icon-star')
            availability_selector = category.selectors.get('availability_selector', '#availability')
            
            # Get product data
            product_data = {}
            
            # Extract price
            try:
                price_elements = self.driver.find_elements(By.CSS_SELECTOR, price_selector)
                if price_elements:
                    price_text = price_elements[0].text.strip() if hasattr(price_elements[0], 'text') else price_elements[0].get_attribute('textContent').strip()
                    product_data['price'] = price_text
            except Exception as e:
                self.logger.warning(f"Error extracting price: {e}")
                product_data['price'] = "N/A"
            
            # Extract rating
            try:
                rating_elements = self.driver.find_elements(By.CSS_SELECTOR, rating_selector)
                if rating_elements:
                    rating_text = rating_elements[0].get_attribute('textContent').strip()
                    product_data['rating'] = rating_text
            except Exception as e:
                self.logger.warning(f"Error extracting rating: {e}")
                product_data['rating'] = "N/A"
            
            # Extract availability
            try:
                availability_elements = self.driver.find_elements(By.CSS_SELECTOR, availability_selector)
                if availability_elements:
                    availability_text = availability_elements[0].text.strip()
                    product_data['availability'] = availability_text
            except Exception as e:
                self.logger.warning(f"Error extracting availability: {e}")
                product_data['availability'] = "N/A"
            
            return product_data
            
        except Exception as e:
            self.logger.error(f"Error processing product {product_url}: {e}")
            return {}
