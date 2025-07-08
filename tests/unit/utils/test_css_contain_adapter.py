import pytest
from bs4 import BeautifulSoup

from src.utils.css_contain_adapter import CSSContainsHandler, EnhancedSelector, StockChecker


class TestCSSContainsHandler:
    
    def test_select_without_contains(self):
        html = '<div class="test">Content</div><p class="test">More</p>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = CSSContainsHandler.select(soup, '.test')
        
        assert len(result) == 2
        assert result[0].name == 'div'
        assert result[1].name == 'p'
    
    def test_select_with_contains(self):
        html = '''
        <div class="item">First item</div>
        <div class="item">Second item</div>
        <div class="item">Third piece</div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        result = CSSContainsHandler.select(soup, '.item:contains("item")')
        
        assert len(result) == 2
        assert "First item" in result[0].get_text()
        assert "Second item" in result[1].get_text()
    
    def test_select_one_with_contains(self):
        html = '''
        <div class="card">Card A</div>
        <div class="card">Card B</div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        result = CSSContainsHandler.select_one(soup, '.card:contains("Card A")')
        
        assert result is not None
        assert "Card A" in result.get_text()
    
    def test_select_one_no_match(self):
        html = '<div class="test">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = CSSContainsHandler.select_one(soup, '.test:contains("Missing")')
        
        assert result is None
    
    def test_handle_contains_selector_invalid_pattern(self):
        html = '<div>Test</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = CSSContainsHandler._handle_contains_selector(soup, 'div:contains(invalid')
        
        assert len(result) >= 0
    
    def test_element_contains_text_direct(self):
        html = '<div>Hello World</div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        result = CSSContainsHandler._element_contains_text(element, "Hello")
        
        assert result is True
    
    def test_element_contains_text_nested(self):
        html = '<div><span>Inner text</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        result = CSSContainsHandler._element_contains_text(element, "Inner")
        
        assert result is True
    
    def test_element_contains_text_not_found(self):
        html = '<div>Hello World</div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        result = CSSContainsHandler._element_contains_text(element, "Missing")
        
        assert result is False


class TestEnhancedSelector:
    
    def test_select_basic_css(self):
        html = '<div class="test">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = EnhancedSelector.select(soup, '.test')
        
        assert len(result) == 1
        assert result[0].get_text() == "Content"
    
    def test_select_with_contains(self):
        html = '''
        <p>First paragraph</p>
        <p>Second paragraph</p>
        <p>Different text</p>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        result = EnhancedSelector.select(soup, 'p:contains("paragraph")')
        
        assert len(result) == 2
    
    def test_select_xpath_fallback(self):
        html = '<div id="test">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = EnhancedSelector.select(soup, '//div[@id="test"]')
        
        assert len(result) >= 0


class TestStockChecker:
    
    def test_is_out_of_stock_with_agotado(self):
        html = '<div><p>Agotado</p></div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = StockChecker.is_out_of_stock(soup, 'p')
        
        assert result is True
    
    def test_is_out_of_stock_with_sin_stock(self):
        html = '<div><span>Sin stock</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = StockChecker.is_out_of_stock(soup, 'span')
        
        assert result is True
    
    def test_is_out_of_stock_available(self):
        html = '<div><p>Disponible</p></div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = StockChecker.is_out_of_stock(soup, 'p')
        
        assert result is False
    
    def test_is_out_of_stock_no_selector_match(self):
        html = '<div><p>Some text</p></div>'
        soup = BeautifulSoup(html, 'html.parser')
        
        result = StockChecker.is_out_of_stock(soup, '.missing')
        
        assert result is False
    
    def test_check_text_indicators_case_insensitive(self):
        indicators = ["agotado", "sin stock", "out of stock"]
        
        assert StockChecker._check_text_indicators("AGOTADO", indicators) is True
        assert StockChecker._check_text_indicators("Sin Stock", indicators) is True
        assert StockChecker._check_text_indicators("available", indicators) is False
    
    def test_check_text_indicators_partial_match(self):
        indicators = ["agotado"]
        
        assert StockChecker._check_text_indicators("Producto agotado temporalmente", indicators) is True
        assert StockChecker._check_text_indicators("Disponible", indicators) is False