import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.la_comarca import LaComarcaScraper
from src.core.category import Category


class TestLaComarcaScraper:

    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'pokemon': {
                    'url': 'https://www.tiendalacomarca.cl/collections/pokemon-singles',
                    'selectors': {
                        'urls_selector': 'a[href*="/products/"]',
                        'title_selector': 'h1.product-single__title',
                        'price_selector': 'span.product-price__price'
                    }
                }
            },
            'batch_size': 5
        }

    @pytest.fixture
    def scraper(self, scraper_config):
        return LaComarcaScraper('la_comarca', scraper_config)

    @pytest.fixture
    def pokemon_category(self):
        return Category(
            'pokemon',
            'https://www.tiendalacomarca.cl/collections/pokemon-singles',
            {
                'urls_selector': 'a[href*="/products/"]',
                'title_selector': 'h1.product-single__title',
                'price_selector': 'span.product-price__price'
            }
        )

    def test_extract_product_urls(self, scraper, pokemon_category):
        html = '''
        <html>
            <body>
                <li class="grid__item">
                    <a href="/products/pikachu-vmax">
                        <div class="grid-view-item__title">Pikachu VMAX</div>
                    </a>
                </li>
                <li class="grid__item">
                    <a href="/products/charizard-gx">
                        <div class="grid-view-item__title">Charizard GX</div>
                    </a>
                </li>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')

        result = scraper.extract_product_urls(soup, pokemon_category)

        assert len(result) == 2
        assert result[0] == ('Pikachu VMAX', 'https://www.tiendalacomarca.cl/products/pikachu-vmax')
        assert result[1] == ('Charizard GX', 'https://www.tiendalacomarca.cl/products/charizard-gx')

    @patch('src.scrapers.la_comarca.LaComarcaScraper.get_page')
    def test_process_product(self, mock_get_page, scraper, pokemon_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup

        result = scraper.process_product('https://test.com/product', pokemon_category)

        assert result is not None
        assert isinstance(result, dict)

    @patch('src.scrapers.la_comarca.LaComarcaScraper.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, pokemon_category):
        mock_get_page.side_effect = Exception('Page load error')

        result = scraper.process_product('https://test.com/product', pokemon_category)

        assert result == {}
