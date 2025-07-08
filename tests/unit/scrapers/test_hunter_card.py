import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.hunter_card_tcg import HunterCardTCG
from src.core.category import Category


class TestHunterCardTCGScraper:
    
    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'pokemon': {
                    'url': 'https://www.huntercardtcg.com/categoria-producto/cartas-sueltas/',
                    'selectors': {
                        'urls_selector': 'a[href*="/producto/"]',
                        'title_selector': 'h2',
                        'price_selector': 'span.woocommerce-Price-amount'
                    }
                }
            },
            'batch_size': 5
        }
    
    @pytest.fixture
    def scraper(self, scraper_config):
        return HunterCardTCG('hunter_card_tcg', scraper_config)
    
    @pytest.fixture
    def pokemon_category(self):
        return Category(
            'pokemon',
            'https://www.huntercardtcg.com/categoria-producto/cartas-sueltas/',
            {
                'urls_selector': 'a[href*="/producto/"]',
                'title_selector': 'h2',
                'price_selector': 'span.woocommerce-Price-amount'
            }
        )
    
    @patch('src.scrapers.hunter_card_tcg.HunterCardTCG.find_elements')
    @patch('src.scrapers.hunter_card_tcg.HunterCardTCG.get_text')
    @patch('src.scrapers.hunter_card_tcg.HunterCardTCG.get_attribute')
    def test_extract_product_urls(self, mock_get_attr, mock_get_text, mock_find_elements, scraper, pokemon_category):
        soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_elements = [Mock(), Mock()]
        mock_find_elements.return_value = mock_elements
        mock_get_text.side_effect = ['Pikachu VMAX', 'Charizard GX']
        mock_get_attr.side_effect = ['/producto/pikachu-vmax', '/producto/charizard-gx']
        
        result = scraper.extract_product_urls(soup, pokemon_category)
        
        assert len(result) == 2
        assert result[0] == ('Pikachu VMAX', 'https://www.huntercardtcg.com/producto/pikachu-vmax')
        assert result[1] == ('Charizard GX', 'https://www.huntercardtcg.com/producto/charizard-gx')
    
    @patch('src.scrapers.hunter_card_tcg.HunterCardTCG.get_page')
    def test_process_product(self, mock_get_page, scraper, pokemon_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @patch('src.scrapers.hunter_card_tcg.HunterCardTCG.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, pokemon_category):
        mock_get_page.side_effect = Exception('Page load error')
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result == {}