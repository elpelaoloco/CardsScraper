import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from src.scrapers.third_impact import ThirdImpact
from src.core.category import Category


class TestThirdImpactScraper:

    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'pokemon': {
                    'url': 'https://www.thirdimpact.cl/collection/pokemon-trading-card-game',
                    'selectors': {
                        'urls_selector': 'a.bs-collection__product-info',
                        'title_selector': 'h1.bs-product__title',
                        'price_selector': 'span.bs-product__final-price'
                    }
                }
            },
            'batch_size': 5
        }

    @pytest.fixture
    def scraper(self, scraper_config):
        return ThirdImpact('third_impact', scraper_config)

    @pytest.fixture
    def pokemon_category(self):
        return Category(
            'pokemon',
            'https://www.thirdimpact.cl/collection/pokemon-trading-card-game',
            {
                'urls_selector': 'a.bs-collection__product-info',
                'title_selector': 'h1.bs-product__title',
                'price_selector': 'span.bs-product__final-price'
            }
        )

    @pytest.fixture
    def sample_category_soup(self):
        html = '''
        <html>
            <body>
                <section class="grid__item">
                    <a class="bs-collection__product-info" href="/product/pikachu-vmax">
                        Pikachu VMAX
                    </a>
                    <a class="bs-collection__product-info" href="/product/charizard-gx">
                        Charizard GX
                    </a>
                </section>
            </body>
        </html>
        '''
        return BeautifulSoup(html, 'html.parser')

    @patch('src.scrapers.third_impact.ThirdImpact.find_elements')
    @patch('src.scrapers.third_impact.ThirdImpact.get_text')
    @patch('src.scrapers.third_impact.ThirdImpact.get_attribute')
    def test_extract_product_urls(self, mock_get_attr, mock_get_text, mock_find_elements, scraper, pokemon_category, sample_category_soup):
        mock_elements = [Mock(), Mock()]
        mock_find_elements.return_value = mock_elements
        mock_get_text.side_effect = ['Pikachu VMAX', 'Charizard GX']
        mock_get_attr.side_effect = ['/product/pikachu-vmax', '/product/charizard-gx']

        result = scraper.extract_product_urls(sample_category_soup, pokemon_category)

        assert len(result) == 2
        assert result[0] == ('Pikachu VMAX', 'https://www.thirdimpact.cl/product/pikachu-vmax')
        assert result[1] == ('Charizard GX', 'https://www.thirdimpact.cl/product/charizard-gx')

    @patch('src.scrapers.third_impact.ThirdImpact.get_page')
    def test_process_product(self, mock_get_page, scraper, pokemon_category):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_get_page.return_value = mock_soup

        result = scraper.process_product('https://test.com/product', pokemon_category)

        assert result is not None
        assert isinstance(result, dict)

    @patch('src.scrapers.third_impact.ThirdImpact.get_page')
    def test_process_product_page_error(self, mock_get_page, scraper, pokemon_category):
        mock_get_page.side_effect = Exception('Page load error')

        result = scraper.process_product('https://test.com/product', pokemon_category)

        assert result == {}
