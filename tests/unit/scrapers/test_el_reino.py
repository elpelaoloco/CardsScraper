import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.el_reino import ElReinoScraper
from src.core.category import Category


class TestElReinoScraper:
    
    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'pokemon': {
                    'url': 'https://elreinodelosduelos.cl/categoria-producto/pokemon-tcg/',
                    'selectors': {
                        'urls_selector': 'a[href*="/producto/"]',
                        'title_selector': 'h1.product-title',
                        'price_selector': 'ins span.woocommerce-Price-amount'
                    }
                }
            },
            'batch_size': 5
        }
    
    @pytest.fixture
    def scraper(self, scraper_config):
        return ElReinoScraper('el_reino', scraper_config)
    
    @pytest.fixture
    def pokemon_category(self):
        return Category(
            'pokemon',
            'https://elreinodelosduelos.cl/categoria-producto/pokemon-tcg/',
            {
                'urls_selector': 'a[href*="/producto/"]',
                'title_selector': 'h1.product-title',
                'price_selector': 'ins span.woocommerce-Price-amount'
            }
        )
    
    @pytest.fixture
    def sample_category_soup(self):
        html = '''
        <html>
            <body>
                <div class="product-element-bottom">
                    <a href="/producto/pokemon-booster-pack">Pokemon Booster Pack</a>
                </div>
                <div class="product-element-bottom">
                    <a href="/producto/pokemon-theme-deck">Pokemon Theme Deck</a>
                </div>
            </body>
        </html>
        '''
        return BeautifulSoup(html, 'html.parser')
    
    @patch('src.scrapers.el_reino.ElReinoScraper.find_elements')
    @patch('src.scrapers.el_reino.ElReinoScraper.get_text')
    @patch('src.scrapers.el_reino.ElReinoScraper.get_attribute')
    def test_extract_product_urls(self, mock_get_attr, mock_get_text, mock_find_elements, scraper, pokemon_category, sample_category_soup):
        mock_elements = [Mock(), Mock()]
        mock_find_elements.return_value = mock_elements
        mock_get_text.side_effect = ['Pokemon Booster Pack', 'Pokemon Theme Deck']
        mock_get_attr.side_effect = ['/producto/pokemon-booster-pack', '/producto/pokemon-theme-deck']
        
        result = scraper.extract_product_urls(sample_category_soup, pokemon_category)
        
        assert len(result) == 2
        assert result[0] == ('Pokemon Booster Pack', 'https://elreinodelosduelos.cl/producto/pokemon-booster-pack')
        assert result[1] == ('Pokemon Theme Deck', 'https://elreinodelosduelos.cl/producto/pokemon-theme-deck')
    
    @patch('src.scrapers.el_reino.ElReinoScraper.get_page')
    def test_process_product(self, mock_get_page, scraper, pokemon_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @patch('src.scrapers.el_reino.ElReinoScraper.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, pokemon_category):
        mock_get_page.side_effect = Exception('Page load error')
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result == {}