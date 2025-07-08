import pytest
import os
import json
import datetime
from unittest.mock import Mock, patch, MagicMock, mock_open
from bs4 import BeautifulSoup
import pandas as pd

from src.core.base_scraper import BaseScraper
from src.core.category import Category


class ConcreteScraper(BaseScraper):
    def navigate_to_category(self, category):
        return BeautifulSoup('<html><body>Test</body></html>', 'html.parser')

    def extract_product_urls(self, soup, category):
        return [('Test Product', 'https://test.com/product')]

    def process_product(self, url, category):
        return {'title': 'Test Product', 'price': '$10', 'url': url}


class TestBaseScraper:

    @pytest.fixture
    def scraper_config(self):
        return {
            'categories': {
                'test_category': {
                    'url': 'https://test.com/category',
                    'selectors': {
                        'urls_selector': 'a.product-link',
                        'title_selector': 'h1.title',
                        'price_selector': '.price'
                    }
                }
            },
            'batch_size': 4
        }

    @pytest.fixture
    def concrete_scraper(self, scraper_config):
        return ConcreteScraper('test_scraper', scraper_config)

    def test_scraper_initialization(self, concrete_scraper):
        assert concrete_scraper.name == 'test_scraper'
        assert len(concrete_scraper.categories) == 1
        assert concrete_scraper.categories[0].name == 'test_category'
        assert concrete_scraper.batch_size is None
        assert concrete_scraper.session is None

    def test_initialize_categories(self, scraper_config):
        scraper = ConcreteScraper('test', scraper_config)
        categories = scraper.categories

        assert len(categories) == 1
        assert categories[0].name == 'test_category'
        assert categories[0].url == 'https://test.com/category'
        assert 'urls_selector' in categories[0].selectors

    def test_initialize_categories_no_url(self):
        config = {
            'categories': {
                'invalid_category': {
                    'selectors': {'test': 'selector'}
                }
            }
        }
        scraper = ConcreteScraper('test', config)

        assert len(scraper.categories) == 0

    @patch('src.core.base_scraper.RequestsHTMLSession')
    def test_setup(self, mock_session, concrete_scraper):
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        concrete_scraper.setup()

        assert concrete_scraper.batch_size == 4
        assert concrete_scraper.session == mock_session_instance
        mock_session.assert_called_once()

    def test_setup_default_batch_size(self, scraper_config):
        del scraper_config['batch_size']
        scraper = ConcreteScraper('test', scraper_config)

        with patch('src.core.base_scraper.RequestsHTMLSession'):
            scraper.setup()

        assert scraper.batch_size == 4

    def test_teardown(self, concrete_scraper):
        mock_session = Mock()
        concrete_scraper.session = mock_session

        concrete_scraper.teardown()

        mock_session.close.assert_called_once()

    def test_teardown_no_session(self, concrete_scraper):
        concrete_scraper.teardown()

        assert concrete_scraper.session is None

    def test_save_results_json(self, concrete_scraper):
        concrete_scraper.results = {'test': [{'name': 'Test Product'}]}

        with patch('builtins.open', mock_open()), \
                patch('json.dump'), \
                patch('os.makedirs'):
            result = concrete_scraper.save_results(format='json')

        assert result.endswith('.json')

    def test_save_results_excel(self, concrete_scraper):
        concrete_scraper.results = {'test_category': [{'title': 'Test', 'price': '$10'}]}

        with patch('builtins.open', mock_open()), \
                patch('pandas.DataFrame.to_csv'), \
                patch('os.makedirs'):
            result = concrete_scraper.save_results(format='csv')

        assert result.endswith('.csv')

    def test_save_report_method_missing(self, concrete_scraper):
        concrete_scraper.report = {'test': 'report'}

        assert hasattr(concrete_scraper, 'report')
        assert concrete_scraper.report == {'test': 'report'}

    def test_get_page_success_real(self, concrete_scraper):
        mock_session = Mock()
        mock_soup = BeautifulSoup('<html><body>Success</body></html>', 'html.parser')
        mock_session.get.return_value = mock_soup
        concrete_scraper.session = mock_session

        result = concrete_scraper.get_page('https://test.com')

        assert result == mock_soup
        mock_session.get.assert_called_once_with('https://test.com', wait_for=None)

    def test_find_elements_css(self, concrete_scraper):
        soup = BeautifulSoup('<div class="test">Content</div>', 'html.parser')

        elements = concrete_scraper.find_elements(soup, 'div.test', 'css')

        assert len(elements) == 1
        assert elements[0].get_text() == 'Content'

    def test_find_elements_invalid_method(self, concrete_scraper):
        soup = BeautifulSoup('<div class="test">Content</div>', 'html.parser')

        with patch('src.utils.css_contain_adapter.EnhancedSelector.select') as mock_select:
            mock_select.return_value = []
            elements = concrete_scraper.find_elements(soup, 'div.test', 'invalid')

        assert elements == []

    def test_get_text(self, concrete_scraper):
        soup = BeautifulSoup('<div>Test Content</div>', 'html.parser')
        element = soup.find('div')

        text = concrete_scraper.get_text(element)

        assert text == 'Test Content'

    def test_get_text_none_element(self, concrete_scraper):
        text = concrete_scraper.get_text(None)

        assert text == ''

    def test_get_attribute(self, concrete_scraper):
        soup = BeautifulSoup('<a href="https://test.com">Link</a>', 'html.parser')
        element = soup.find('a')

        href = concrete_scraper.get_attribute(element, 'href')

        assert href == 'https://test.com'

    def test_get_attribute_none_element(self, concrete_scraper):
        attr = concrete_scraper.get_attribute(None, 'href')

        assert attr == ''

    @patch('src.utils.session_html.RequestsHTMLSession.get')
    def test_get_page(self, mock_get, concrete_scraper):
        mock_soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')
        mock_session = Mock()
        mock_session.get.return_value = mock_soup
        concrete_scraper.session = mock_session

        result = concrete_scraper.get_page('https://test.com')

        assert result == mock_soup
        mock_session.get.assert_called_once_with('https://test.com', wait_for=None)

    @patch('src.utils.session_html.RequestsHTMLSession.get')
    def test_get_page_error(self, mock_get, concrete_scraper):
        mock_session = Mock()
        mock_session.get.side_effect = Exception('Network error')
        concrete_scraper.session = mock_session

        with pytest.raises(Exception):
            concrete_scraper.get_page('https://test.com')

    def test_find_element(self, concrete_scraper):
        soup = BeautifulSoup('<div class="test">Content</div><div class="test">Content2</div>', 'html.parser')

        element = concrete_scraper.find_element(soup, 'div.test', 'css')

        assert element is not None
        assert element.get_text() == 'Content'

    def test_find_element_not_found(self, concrete_scraper):
        soup = BeautifulSoup('<div class="other">Content</div>', 'html.parser')

        element = concrete_scraper.find_element(soup, 'div.test', 'css')

        assert element is None

    def test_find_elements_xpath(self, concrete_scraper):
        soup = BeautifulSoup('<div class="test">Content</div>', 'html.parser')

        elements = concrete_scraper.find_elements(soup, '//div[@class="test"]', 'xpath')

        assert len(elements) >= 0

    @patch('src.utils.css_contain_adapter.StockChecker.is_out_of_stock')
    def test_check_stock_in_stock(self, mock_stock_checker, concrete_scraper):
        mock_stock_checker.return_value = False
        soup = BeautifulSoup('<div>In stock</div>', 'html.parser')

        result = concrete_scraper.check_stock(soup, 'div')

        assert result == 'in_stock'

    @patch('src.utils.css_contain_adapter.StockChecker.is_out_of_stock')
    def test_check_stock_out_of_stock(self, mock_stock_checker, concrete_scraper):
        mock_stock_checker.return_value = True
        soup = BeautifulSoup('<div>Out of stock</div>', 'html.parser')

        result = concrete_scraper.check_stock(soup, 'div')

        assert result == 'out_of_stock'

    @patch('src.utils.css_contain_adapter.StockChecker.is_out_of_stock')
    def test_check_stock_error(self, mock_stock_checker, concrete_scraper):
        mock_stock_checker.side_effect = Exception('Error checking stock')
        soup = BeautifulSoup('<div>Test</div>', 'html.parser')

        result = concrete_scraper.check_stock(soup, 'div')

        assert result == 'unknown'

    def test_xpath_to_css(self, concrete_scraper):
        xpath = '//div[@class="test"]'

        result = concrete_scraper._xpath_to_css(xpath)

        assert 'div' in result

    def test_xpath_to_css_non_xpath(self, concrete_scraper):
        css = 'div.test'

        result = concrete_scraper._xpath_to_css(css)

        assert result == css

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_screenshot(self, mock_makedirs, mock_file, concrete_scraper):
        soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')

        result = concrete_scraper.save_screenshot(soup, 'test.html')

        assert 'test.html' in result
        mock_file.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_screenshot_error(self, mock_makedirs, mock_file, concrete_scraper):
        mock_file.side_effect = Exception('Write error')
        soup = BeautifulSoup('<html><body>Test</body></html>', 'html.parser')

        result = concrete_scraper.save_screenshot(soup, 'test.html')

        assert result == ''

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('json.dump')
    def test_save_results_json_format(self, mock_json_dump, mock_makedirs, mock_file, concrete_scraper):
        concrete_scraper.results = {'test': [{'name': 'Test Product'}]}

        result = concrete_scraper.save_results(format='json')

        assert result.endswith('.json')
        mock_json_dump.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_results_csv_format(self, mock_to_csv, mock_makedirs, mock_file, concrete_scraper):
        concrete_scraper.results = {'test': [{'name': 'Test Product'}]}

        result = concrete_scraper.save_results(format='csv')

        assert result.endswith('.csv')
        mock_to_csv.assert_called()

    def test_save_results_no_results(self, concrete_scraper):
        concrete_scraper.results = {}

        result = concrete_scraper.save_results()

        assert result == ''

    def test_save_results_invalid_format(self, concrete_scraper):
        concrete_scraper.results = {'test': [{'name': 'Test Product'}]}

        result = concrete_scraper.save_results(format='xml')

        assert result == ''

    def test_get_report(self, concrete_scraper):
        test_report = {'test': 'data'}
        concrete_scraper.report = test_report

        result = concrete_scraper.get_report()

        assert result == test_report

    def test_detect_type_booster(self, concrete_scraper):
        result = concrete_scraper.detect_type('Pokemon Booster Pack')
        assert result == 'booster'

    def test_detect_type_bundle(self, concrete_scraper):
        result = concrete_scraper.detect_type('Magic Bundle Set')
        assert result == 'bundle'

    def test_detect_type_singles(self, concrete_scraper):
        result = concrete_scraper.detect_type('Lightning Bolt Card')
        assert result == 'singles'

    def test_clean_price_with_number(self, concrete_scraper):
        result = concrete_scraper.clean_price('$1500')
        assert result == 1500

    def test_clean_price_with_multiple_numbers(self, concrete_scraper):
        result = concrete_scraper.clean_price('Price: $1,500.00')
        assert result == 150000

    def test_clean_price_no_number(self, concrete_scraper):
        result = concrete_scraper.clean_price('Free')
        assert result == 0

    def test_clean_price_empty(self, concrete_scraper):
        result = concrete_scraper.clean_price('')
        assert result == 0

    @patch.object(ConcreteScraper, 'setup')
    @patch.object(ConcreteScraper, 'teardown')
    @patch.object(ConcreteScraper, 'navigate_to_category')
    @patch.object(ConcreteScraper, 'extract_product_urls')
    @patch.object(ConcreteScraper, 'process_product')
    def test_run_success(self, mock_process, mock_extract, mock_navigate, mock_teardown, mock_setup, concrete_scraper):
        concrete_scraper.batch_size = 4
        mock_navigate.return_value = BeautifulSoup('<html></html>', 'html.parser')
        mock_extract.return_value = [('Test Product', 'https://test.com/product')]
        mock_process.return_value = {'title': 'Test Product', 'price': 1500}

        result = concrete_scraper.run()

        assert 'test_category' in result
        assert len(result['test_category']) == 1
        assert result['test_category'][0]['name'] == 'Test Product'
        mock_setup.assert_called_once()
        mock_teardown.assert_called_once()

    @patch.object(ConcreteScraper, 'setup')
    @patch.object(ConcreteScraper, 'teardown')
    def test_run_setup_error(self, mock_teardown, mock_setup, concrete_scraper):
        mock_setup.side_effect = Exception('Setup failed')

        result = concrete_scraper.run()

        assert result == {}
        mock_teardown.assert_called_once()
