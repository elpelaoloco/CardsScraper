import time
from typing import List, Tuple, Dict, Any
from src.core.base_scraper import BaseScraper
from src.core.category import Category
from selenium.webdriver.common.by import By

class LaComarcaScraper(BaseScraper):
    def navigate_to_category(self, category: Category) -> None:
        self.logger.info(f"Navigating to {category.url}")
        self.driver.get(category.url)
        time.sleep(self.config.get('page_load_delay', 2))

    def extract_product_urls(self, category: Category) -> List[Tuple[str, str]]:
        containers_xpath = "//li[contains(@class, 'grid__item')]"
        self.wait_for_element(containers_xpath)

        containers = self.driver.find_elements(By.XPATH, containers_xpath)
        urls = []

        for container in containers:
            try:
                # URL del producto
                a_tag = container.find_element(By.XPATH, ".//a[contains(@href, '/products/')]")
                url = a_tag.get_attribute("href")

                # Nombre limpio
                name_el = container.find_element(By.XPATH, ".//div[contains(@class, 'grid-view-item__title')]")
                name = name_el.text.strip()

                if not name or not url or "ULTIMAS UNIDADES" in name.upper():
                    continue

                urls.append((name, url))
            except Exception as e:
                self.logger.warning(f"Error processing product container: {e}")

        return urls


    def process_product(self, product_url: str, category: Category) -> Dict[str, Any]:
        self.driver.get(product_url)
        time.sleep(self.config.get('page_load_delay', 2))

        data = {}

        # Extraer nombre desde el h1
        try:
            name_el = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'product-single__title')]")
            data["name"] = name_el.text.strip()
        except Exception as e:
            self.logger.warning(f"No name found: {e}")
            data["name"] = "undefined"

        # Extraer precio
        price_sel = category.selectors.get('price_selector')
        if price_sel:
            try:
                price_el = self.driver.find_element(By.XPATH, price_sel)
                price_text = price_el.text.strip()
                if price_text:
                    data["price"] = price_text
                else:
                    self.logger.warning(f"Empty price found at {product_url}")
                    data["price"] = ""
            except Exception as e:
                self.logger.warning(f"No price found: {e}")
                data["price"] = ""
        else:
            data["price"] = ""
        # Imagen
        image_selector = category.selectors.get('image_selector')
        if image_selector:
            try:
                image_el = self.driver.find_element(By.XPATH, image_selector)
                image_url = image_el.get_attribute("data-zoom")
                data["img_url"] = "https:"+image_url
            except Exception as e:
                self.logger.warning(f"Image not found: {e}")
                data["img_url"] = ""
        else:
            data["img_url"] = ""


        return data
