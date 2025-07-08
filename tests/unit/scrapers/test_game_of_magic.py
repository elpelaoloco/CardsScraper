import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.game_of_magic import GameOfMagicScraper
from src.core.category import Category


class TestGameOfMagicScraper:
    
    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'magic': {
                    'url': 'https://www.gameofmagictienda.cl/collection/magic',
                    'selectors': {
                        'product_selector': 'div.bs-collection__product',
                        'urls_selector': 'a[href*="/product/"]',
                        'title_selector': 'h1.bs-product__title',
                        'price_selector': 'span.bs-product__final-price'
                    }
                }
            },
            'batch_size': 5
        }
    
    @pytest.fixture
    def scraper(self, scraper_config):
        return GameOfMagicScraper('game_of_magic', scraper_config)
    
    @pytest.fixture
    def magic_category(self):
        return Category(
            'magic',
            'https://www.gameofmagictienda.cl/collection/magic',
            {
                'product_selector': 'div.bs-collection__product',
                'urls_selector': 'a[href*="/product/"]',
                'title_selector': 'h1.bs-product__title',
                'price_selector': 'span.bs-product__final-price'
            }
        )
    
    def test_extract_product_urls(self, scraper, magic_category):
        html = '''
        <html>
            <body>
                <div class="bs-collection__product">
                    <a href="/product/lightning-bolt" title="Lightning Bolt">Lightning Bolt</a>
                </div>
                <div class="bs-collection__product">
                    <a href="/product/counterspell" title="Counterspell">Counterspell</a>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        result = scraper.extract_product_urls(soup, magic_category)
        
        assert len(result) == 2
        assert result[0] == ('Lightning Bolt', 'https://www.gameofmagictienda.cl/product/lightning-bolt')
        assert result[1] == ('Counterspell', 'https://www.gameofmagictienda.cl/product/counterspell')
    
    @patch('src.scrapers.game_of_magic.GameOfMagicScraper.get_page')
    def test_process_product(self, mock_get_page, scraper, magic_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup
        
        result = scraper.process_product('https://test.com/product', magic_category)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @patch('src.scrapers.game_of_magic.GameOfMagicScraper.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, magic_category):
        mock_get_page.side_effect = Exception('Page load error')
        
        result = scraper.process_product('https://test.com/product', magic_category)
        
        assert result == {}