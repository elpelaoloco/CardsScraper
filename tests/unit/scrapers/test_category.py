import pytest
from src.core.category import Category


class TestCategory:
    
    def test_category_initialization(self):
        selectors = {
            'urls_selector': 'a.product-link',
            'title_selector': 'h1.title',
            'price_selector': '.price'
        }
        category = Category('pokemon', 'https://example.com/pokemon', selectors)
        
        assert category.name == 'pokemon'
        assert category.url == 'https://example.com/pokemon'
        assert category.selectors == selectors
    
    def test_category_with_empty_selectors(self):
        category = Category('magic', 'https://example.com/magic', {})
        
        assert category.name == 'magic'
        assert category.url == 'https://example.com/magic'
        assert category.selectors == {}
    
    def test_get_selector_valid_key(self):
        selectors = {
            'price_selector': "//span[@class='price']",
            'title_selector': "//h1"
        }
        category = Category('pokemon', 'https://example.com/pokemon', selectors)
        
        selector = category.selectors.get('price_selector')
        assert selector == "//span[@class='price']"
    
    def test_get_selector_invalid_key_returns_none(self):
        selectors = {
            'price_selector': "//span[@class='price']",
            'title_selector': "//h1"
        }
        category = Category('pokemon', 'https://example.com/pokemon', selectors)
        
        selector = category.selectors.get('nonexistent_selector')
        assert selector is None
    
    def test_category_attribute_access(self):
        selectors = {'test_selector': 'value'}
        category = Category('yugioh', 'https://example.com/yugioh', selectors)
        
        assert category.name == 'yugioh'
        assert category.url == 'https://example.com/yugioh'
        assert category.selectors == selectors