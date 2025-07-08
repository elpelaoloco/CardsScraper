import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from src.scrapers.card_universe import CardUniverseScraper
from src.core.category import Category


class TestCardUniverseScraper:
    
    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'magic': {
                    'url': 'https://carduniverse.cl/collections/magic-the-gathering',
                    'selectors': {
                        'urls_selector': 'a.prod-th',
                        'title_selector': 'h1.product-title',
                        'price_selector': 'div.price span.money',
                        'description_selector': 'blockquote ul:first-child',
                        'image_selector': 'div.product-single__photo img'
                    }
                }
            },
            'batch_size': 5
        }
    
    @pytest.fixture
    def scraper(self, scraper_config):
        return CardUniverseScraper('card_universe', scraper_config)
    
    @pytest.fixture
    def magic_category(self):
        return Category(
            'magic',
            'https://carduniverse.cl/collections/magic-the-gathering',
            {
                'urls_selector': 'a.prod-th',
                'title_selector': 'h1.product-title',
                'price_selector': 'div.price span.money',
                'description_selector': 'blockquote ul:first-child',
                'image_selector': 'div.product-single__photo img'
            }
        )
    
    @pytest.fixture
    def sample_category_soup(self):
        html = '''
        <html>
            <body>
                <div class="product-grid">
                    <a class="prod-th" href="/products/lightning-bolt">
                        <span class="product-title">
                            <span class="title">Lightning Bolt</span>
                        </span>
                    </a>
                    <a class="prod-th" href="/products/counterspell">
                        <span class="product-title">
                            <span class="title">Counterspell</span>
                        </span>
                    </a>
                </div>
            </body>
        </html>
        '''
        return BeautifulSoup(html, 'html.parser')
    
    @patch('src.scrapers.card_universe.CardUniverseScraper.find_elements')
    @patch('src.scrapers.card_universe.CardUniverseScraper.get_text')
    @patch('src.scrapers.card_universe.CardUniverseScraper.get_attribute')
    def test_extract_product_urls(self, mock_get_attr, mock_get_text, mock_find_elements, scraper, magic_category, sample_category_soup):
        mock_elements = [Mock(), Mock()]
        mock_find_elements.return_value = mock_elements
        mock_get_text.side_effect = ['Lightning Bolt\nDetails', 'Counterspell\nDetails']
        mock_get_attr.side_effect = ['/products/lightning-bolt', '/products/counterspell']
        
        result = scraper.extract_product_urls(sample_category_soup, magic_category)
        
        assert len(result) == 2
        assert result[0] == ('Lightning Bolt', 'https://carduniverse.cl/products/lightning-bolt')
        assert result[1] == ('Counterspell', 'https://carduniverse.cl/products/counterspell')
    
    @patch('src.scrapers.card_universe.CardUniverseScraper.get_page')
    def test_process_product(self, mock_get_page, scraper, magic_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup
        
        result = scraper.process_product('https://test.com/product', magic_category)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @patch('src.scrapers.card_universe.CardUniverseScraper.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, magic_category):
        mock_get_page.side_effect = Exception('Page load error')
        
        result = scraper.process_product('https://test.com/product', magic_category)
        
        assert result == {}