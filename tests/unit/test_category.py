import unittest
from src.core.category import Category


class TestCategory(unittest.TestCase):
    def setUp(self):
        self.name = "pokemon"
        self.url = "https://example.com/pokemon"
        self.selectors = {
            "price_selector": "//span[@class='price']",
            "title_selector": "//h1"
        }

    def test_category_initialization(self):
        category = Category(self.name, self.url, self.selectors)
        print(
            f"\n✔ Inicialización exitosa para categoría '{category.name}' con URL '{category.url}'")
        self.assertEqual(category.name, self.name,
                         "El nombre de la categoría no coincide")
        self.assertEqual(category.url, self.url, "La URL de la categoría no coincide")
        self.assertEqual(category.selectors, self.selectors,
                         "Los selectores no coinciden")

    def test_get_selector_valid_key(self):
        category = Category(self.name, self.url, self.selectors)
        selector = category.selectors.get("price_selector")
        print(f"✔ Selector de precio encontrado: {selector}")
        self.assertEqual(selector, "//span[@class='price']",
                         "Selector incorrecto para 'price_selector'")

    def test_get_selector_invalid_key_returns_none(self):
        category = Category(self.name, self.url, self.selectors)
        selector = category.selectors.get("nonexistent_selector")
        print(f"✔ Selector inexistente correctamente manejado: {selector}")
        self.assertIsNone(
            selector, "Se esperaba None al consultar un selector inexistente")


if __name__ == '__main__':
    unittest.main(verbosity=2)
