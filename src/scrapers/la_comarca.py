import time
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup
from src.core.base_scraper import BaseScraper
from src.core.category import Category


class LaComarcaScraper(BaseScraper):

    def navigate_to_category(self, category: Category) -> BeautifulSoup:
        self.logger.info(f"Navigating to {category.url}")
        wait_for = category.selectors.get('urls_selector')
        soup = self.get_page(category.url, wait_for=wait_for)
        return soup

    def extract_product_urls(self, soup: BeautifulSoup, category: Category) -> List[Tuple[str, str]]:

        containers = soup.select("li.grid__item")
        urls = []

        for container in containers:
            try:

                a_tag = container.select_one("a[href*='/products/']")
                if not a_tag:
                    continue

                url = a_tag.get('href', '')

                name_el = container.select_one("div.grid-view-item__title")
                if name_el:
                    name = name_el.get_text(strip=True)
                else:
                    continue

                if not name or not url or "ULTIMAS UNIDADES" in name.upper():
                    continue

                if url.startswith('/'):
                    base_url = category.url.split('/')[0] + '//' + category.url.split('/')[2]
                    url = base_url + url

                urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error processing product container: {e}")

        return urls

    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        try:
            soup = self.get_page(product_url)
        except Exception as e:
            self.logger.error(f"Failed to load product page {product_url}: {e}")
            return {}

        data = {}

        try:
            name_el = soup.select_one("h1.product-single__title")
            if name_el:
                data["name"] = name_el.get_text(strip=True)
            else:
                data["name"] = "undefined"
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        price_sel = category.selectors.get('price_selector')
        if price_sel:
            try:
                if price_sel.startswith('//'):
                    price_el = self.find_element(soup, price_sel, 'xpath')
                else:
                    price_el = self.find_element(soup, price_sel, 'css')

                if price_el:
                    price_text = self.get_text(price_el)
                    data["price"] = price_text if price_text else ""
                else:
                    self.logger.warning(f"Empty price found at {product_url}")
                    data["price"] = ""
            except Exception as e:
                self.logger.warning(f"No price found: {e}")
                data["price"] = ""
        else:
            data["price"] = ""

        image_selector = category.selectors.get('image_selector')
        if image_selector:
            try:
                if image_selector.startswith('//'):
                    image_el = self.find_element(soup, image_selector, 'xpath')
                else:
                    image_el = self.find_element(soup, image_selector, 'css')

                if image_el:
                    image_url = image_el.get("data-zoom", "")
                    if image_url:
                        data["img_url"] = "https:" + image_url
                    else:
                        data["img_url"] = ""
                else:
                    data["img_url"] = ""
            except Exception as e:
                self.logger.warning(f"Image not found: {e}")
                data["img_url"] = ""
        else:
            data["img_url"] = ""

        return data
