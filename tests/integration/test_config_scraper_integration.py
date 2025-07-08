import pytest
import os
import json
from unittest.mock import patch, Mock

from src.core.scraper_manager import ScraperManager
from src.core.scraper_factory import ScraperFactory


class TestConfigScraperIntegration:

    @pytest.fixture(scope="class")
    def real_test_config_path(self):
        return "configs/test_config.json"

    @pytest.fixture(scope="class")
    def real_config_data(self, real_test_config_path):
        with open(real_test_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def test_config_loads_successfully(self, real_test_config_path):

        manager = ScraperManager(real_test_config_path)

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'scrapers')
        assert isinstance(manager.config, dict)
        assert 'scrapers' in manager.config

    def test_all_scrapers_initialize_from_config(self, real_test_config_path, real_config_data):

        manager = ScraperManager(real_test_config_path)

        expected_scrapers = list(real_config_data['scrapers'].keys())
        actual_scrapers = list(manager.scrapers.keys())

        assert len(actual_scrapers) == len(expected_scrapers)

        for scraper_name in expected_scrapers:
            assert scraper_name in actual_scrapers
            assert manager.scrapers[scraper_name] is not None

    def test_scraper_factory_creates_all_types(self, real_config_data):

        unique_types = set()
        for scraper_config in real_config_data['scrapers'].values():
            unique_types.add(scraper_config['type'])

        for scraper_type in unique_types:
            sample_config = {
                'type': scraper_type,
                'categories': {
                    'test': {
                        'url': 'https://test.com',
                        'selectors': {
                            'product_selector': '.product',
                            'urls_selector': 'a.link'
                        }
                    }
                }
            }

            scraper = ScraperFactory.create_scraper('test_scraper', sample_config)

            assert scraper is not None
            assert hasattr(scraper, 'name')
            assert hasattr(scraper, 'categories')
            assert len(scraper.categories) == 1

    def test_scrapers_have_required_methods(self, real_test_config_path):

        manager = ScraperManager(real_test_config_path)

        required_methods = [
            'navigate_to_category',
            'extract_product_urls',
            'process_product',
            'setup',
            'teardown',
            'run'
        ]

        for scraper_name, scraper in manager.scrapers.items():
            for method_name in required_methods:
                assert hasattr(scraper, method_name), f"Scraper {scraper_name} missing method {method_name}"
                assert callable(getattr(scraper, method_name))

    def test_scrapers_categories_configuration(self, real_test_config_path, real_config_data):

        manager = ScraperManager(real_test_config_path)

        for scraper_name, scraper_config in real_config_data['scrapers'].items():
            scraper = manager.scrapers[scraper_name]
            expected_categories = list(scraper_config['categories'].keys())
            actual_categories = [cat.name for cat in scraper.categories]

            assert len(actual_categories) == len(expected_categories)

            for expected_cat in expected_categories:
                assert expected_cat in actual_categories

                category = next(cat for cat in scraper.categories if cat.name == expected_cat)

                assert hasattr(category, 'url')
                assert hasattr(category, 'selectors')
                assert category.url.startswith('http')
                assert len(category.selectors) > 0

    def test_scrapers_selectors_validation(self, real_test_config_path, real_config_data):

        manager = ScraperManager(real_test_config_path)

        required_selectors = ['product_selector', 'urls_selector']

        for scraper_name, scraper_config in real_config_data['scrapers'].items():
            scraper = manager.scrapers[scraper_name]

            for category in scraper.categories:
                for required_selector in required_selectors:
                    assert required_selector in category.selectors, \
                        f"Scraper {scraper_name}, category {category.name} missing {required_selector}"

                    selector_value = category.selectors[required_selector]
                    assert isinstance(selector_value, str)
                    assert len(selector_value) > 0

    @patch('src.core.base_scraper.RequestsHTMLSession')
    def test_scrapers_can_setup_and_teardown(self, mock_session_class, real_test_config_path):

        mock_session = Mock()
        mock_session_class.return_value = mock_session

        manager = ScraperManager(real_test_config_path)

        for scraper_name, scraper in manager.scrapers.items():
            try:
                scraper.setup()
                assert scraper.session is not None
                assert hasattr(scraper, 'batch_size')

                scraper.teardown()
                mock_session.close.assert_called()

                mock_session.reset_mock()

            except Exception as e:
                pytest.fail(f"Scraper {scraper_name} failed setup/teardown: {e}")

    def test_config_stores_coverage(self, real_config_data):

        scrapers = real_config_data['scrapers']
        scraper_names = list(scrapers.keys())

        assert len(scraper_names) >= 5, f"Expected at least 5 stores, found {len(scraper_names)}"

        expected_stores = ['card_universe', 'thirdimpact', 'la_comarca']

        for expected_store in expected_stores:
            assert any(expected_store in name for name in scraper_names), \
                f"Expected store type {expected_store} not found in config"

    def test_config_games_coverage(self, real_config_data):

        all_categories = set()

        for scraper_config in real_config_data['scrapers'].values():
            categories = scraper_config.get('categories', {})
            all_categories.update(categories.keys())

        expected_games = ['pokemon', 'magic', 'yugioh']

        for expected_game in expected_games:
            assert expected_game in all_categories, \
                f"Expected game {expected_game} not found in any scraper config"

    def test_scraper_manager_report_functionality(self, real_test_config_path):

        manager = ScraperManager(real_test_config_path)

        assert hasattr(manager, 'report')
        assert isinstance(manager.report, dict)

        report = manager.get_report()
        assert isinstance(report, dict)

    def test_config_url_accessibility(self, real_config_data):

        for scraper_name, scraper_config in real_config_data['scrapers'].items():
            categories = scraper_config.get('categories', {})

            for category_name, category_config in categories.items():
                url = category_config.get('url', '')

                assert url.startswith('http'), \
                    f"Invalid URL in {scraper_name}.{category_name}: {url}"

                assert '://' in url, \
                    f"Malformed URL in {scraper_name}.{category_name}: {url}"

                assert len(url.split('/')[2]) > 3, \
                    f"Suspicious domain in {scraper_name}.{category_name}: {url}"

    def test_scraper_specific_implementations(self, real_test_config_path):

        manager = ScraperManager(real_test_config_path)

        scraper_classes = set()

        for scraper_name, scraper in manager.scrapers.items():
            scraper_class = type(scraper).__name__

            assert scraper_class not in scraper_classes or scraper_class == 'BaseScraper', \
                f"Duplicate scraper class found: {scraper_class}"

            scraper_classes.add(scraper_class)

            assert scraper.name == scraper_name

            assert len(scraper.categories) > 0
