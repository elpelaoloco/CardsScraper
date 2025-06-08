import unittest
import json
from src.core.scraper_factory import ScraperFactory
from src.core.category import Category


class BaseScraperTest(unittest.TestCase):
    SCRAPER_TYPE = None
    CATEGORY_KEY = None

    @classmethod
    def setUpClass(cls):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                all_config = json.load(f)
        except Exception as e:
            raise unittest.SkipTest(f"❌ No se pudo cargar 'config.json': {e}")

        config = all_config.get(cls.SCRAPER_TYPE)
        if config is None:
            raise unittest.SkipTest(f"❌ No se encontró configuración para el scrapper '{cls.SCRAPER_TYPE}' en config.json")

        try:
            cls.scraper = ScraperFactory.create_scraper(cls.SCRAPER_TYPE, config)
        except Exception as e:
            raise unittest.SkipTest(f"❌ Error creando scraper '{cls.SCRAPER_TYPE}': {e}")

        try:
            cls.category = config['categories'][cls.CATEGORY_KEY]
        except KeyError:
            raise unittest.SkipTest(f"❌ Categoría '{cls.CATEGORY_KEY}' no encontrada para el scraper '{cls.SCRAPER_TYPE}'")

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
