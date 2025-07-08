import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.guild_dreams import GuildDreamsScraper
from src.core.category import Category


class TestGuildDreamsScraper:
    
    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'pokemon': {
                    'url': 'https://www.guildreams.com/collection/pokemon',
                    'selectors': {
                        'urls_selector': 'a[href*="/product/"]',
                        'title_selector': 'h1.h2',
                        'price_selector': 'span.h2, div.h3'
                    }
                }
            },
            'batch_size': 5
        }
    
    @pytest.fixture
    def scraper(self, scraper_config):
        return GuildDreamsScraper('guild_dreams', scraper_config)
    
    @pytest.fixture
    def pokemon_category(self):
        return Category(
            'pokemon',
            'https://www.guildreams.com/collection/pokemon',
            {
                'urls_selector': 'a[href*="/product/"]',
                'title_selector': 'h1.h2',
                'price_selector': 'span.h2, div.h3'
            }
        )
    
    @patch('src.scrapers.guild_dreams.GuildDreamsScraper.find_elements')
    @patch('src.scrapers.guild_dreams.GuildDreamsScraper.get_text')
    @patch('src.scrapers.guild_dreams.GuildDreamsScraper.get_attribute')
    def test_extract_product_urls(self, mock_get_attr, mock_get_text, mock_find_elements, scraper, pokemon_category):
        soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_elements = [Mock(), Mock()]
        mock_find_elements.return_value = mock_elements
        mock_get_text.side_effect = ['Pikachu VMAX', 'Charizard GX']
        mock_get_attr.side_effect = ['/product/pikachu-vmax', '/product/charizard-gx']
        
        result = scraper.extract_product_urls(soup, pokemon_category)
        
        assert len(result) == 2
        assert result[0] == ('Pikachu VMAX', 'https://www.guildreams.com/product/pikachu-vmax')
        assert result[1] == ('Charizard GX', 'https://www.guildreams.com/product/charizard-gx')
    
    @patch('src.scrapers.guild_dreams.GuildDreamsScraper.get_page')
    def test_process_product(self, mock_get_page, scraper, pokemon_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @patch('src.scrapers.guild_dreams.GuildDreamsScraper.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, pokemon_category):
        mock_get_page.side_effect = Exception('Page load error')
        
        result = scraper.process_product('https://test.com/product', pokemon_category)
        
        assert result == {}