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

    def test_init_custom_attributes(self, scraper_config):
        scraper = GuildDreamsScraper('guild_dreams', scraper_config)

        assert hasattr(scraper, 'url_to_image')
        assert isinstance(scraper.url_to_image, dict)
        assert len(scraper.url_to_image) == 0

    def test_url_to_image_mapping(self, scraper):
        test_url = 'https://test.com/product1'
        test_image = 'https://test.com/image1.jpg'

        scraper.url_to_image[test_url] = test_image

        assert scraper.url_to_image[test_url] == test_image
        assert len(scraper.url_to_image) == 1

    def test_url_to_image_multiple_mappings(self, scraper):
        mappings = {
            'https://test.com/product1': 'https://test.com/image1.jpg',
            'https://test.com/product2': 'https://test.com/image2.jpg',
            'https://test.com/product3': 'https://test.com/image3.jpg'
        }

        for url, image in mappings.items():
            scraper.url_to_image[url] = image

        assert len(scraper.url_to_image) == 3

        for url, expected_image in mappings.items():
            assert scraper.url_to_image[url] == expected_image

    def test_url_to_image_persistence_across_calls(self, scraper):
        scraper.url_to_image['test_url'] = 'test_image'

        scraper.url_to_image['another_url'] = 'another_image'

        assert scraper.url_to_image['test_url'] == 'test_image'
        assert scraper.url_to_image['another_url'] == 'another_image'
        assert len(scraper.url_to_image) == 2
