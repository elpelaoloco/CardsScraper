import unittest
import json
import os
from src.core.scraper_factory import ScraperFactory
from src.core.category import Category


class BaseScraperTest(unittest.TestCase):
    SCRAPER_TYPE = "la_comarca"
    CATEGORY_KEY = "pokemon"
    CONFIG_PATH = os.path.join(os.path.dirname(__file__),"..", "..", "configs", "scrapers_config.json")

    @classmethod
    def setUpClass(cls):
        with open(cls.CONFIG_PATH, "r", encoding="utf-8") as f:
            all_config = json.load(f)

        scraper_config = all_config["scrapers"].get(cls.SCRAPER_TYPE)
        
        if not scraper_config:
            raise ValueError(f"No se encontró configuración para el tipo '{cls.SCRAPER_TYPE}'")

        cls.scraper = ScraperFactory.create_scraper(cls.SCRAPER_TYPE, scraper_config)
        cls.category = scraper_config["categories"].get(cls.CATEGORY_KEY)

        if not cls.category:
            raise ValueError(f"No se encontró categoría '{cls.CATEGORY_KEY}' para el scraper '{cls.SCRAPER_TYPE}'")
    def test_url_is_valid(self):
        self.assertTrue(self.category['url'].startswith('http'), f"⚠️ URL inválida: {self.category['url']}")

    def test_product_parameters_exist(self):
        selectors = self.category.get('selectors', {})
        required_keys = ['urls_selector', 'price_selector', 'title_selector']

        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, selectors, f"❌ Falta el selector requerido '{key}' en la categoría")
                self.assertTrue(selectors[key], f"❌ Selector '{key}' está vacío")

    def test_product_selector_priority(self):
        # Este test evalúa si el 'urls_selector' es parte del 'product_selector' o está bien estructurado
        product_selector = self.category['selectors'].get('product_selector', '')
        urls_selector = self.category['selectors'].get('urls_selector', '')

        self.assertTrue(product_selector or urls_selector, "❌ No hay selectores definidos para ubicar productos.")
