import pytest
import json
import yaml
import os
import tempfile
import datetime
from unittest.mock import Mock, patch, mock_open, MagicMock, call
from typing import Dict, Any, List

from src.core.scraper_manager import ScraperManager
from src.core.base_scraper import BaseScraper


class MockScraper(BaseScraper):

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.mock_results = {}
        self.mock_report = {}
        self.run_called = False
        self.get_report_called = False

    def navigate_to_category(self, category):
        from bs4 import BeautifulSoup
        return BeautifulSoup("<html></html>", 'html.parser')

    def extract_product_urls(self, soup, category) -> List[str]:
        return []

    def process_product(self, product_url: str) -> Dict[str, Any]:
        return {}

    def run(self) -> Dict[str, List[Dict[str, Any]]]:
        self.run_called = True
        return self.mock_results

    def get_report(self) -> Dict[str, Any]:
        self.get_report_called = True
        return self.mock_report

    def set_mock_results(self, results: Dict[str, List[Dict[str, Any]]]):
        self.mock_results = results

    def set_mock_report(self, report: Dict[str, Any]):
        self.mock_report = report


class TestScraperManager:

    @pytest.fixture
    def sample_json_config(self):
        return {
            "scrapers": {
                "test_scraper_1": {
                    "type": "guild_dreams",
                    "base_url": "https://example1.com",
                    "categories": {
                        "magic": {"url": "https://example1.com/magic", "active": True}
                    }
                },
                "test_scraper_2": {
                    "type": "card_universe",
                    "base_url": "https://example2.com",
                    "categories": {
                        "pokemon": {"url": "https://example2.com/pokemon", "active": True}
                    }
                }
            }
        }

    @pytest.fixture
    def sample_yaml_config(self):
        return {
            "scrapers": {
                "yaml_scraper": {
                    "type": "hunter_card_tcg",
                    "base_url": "https://yaml-example.com",
                    "categories": {
                        "yugioh": {"url": "https://yaml-example.com/yugioh", "active": True}
                    }
                }
            }
        }

    @pytest.fixture
    def temp_json_config_file(self, sample_json_config):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_json_config, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    @pytest.fixture
    def temp_yaml_config_file(self, sample_yaml_config):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_yaml_config, f)
            temp_file = f.name
        yield temp_file
        os.unlink(temp_file)

    def test_init_with_json_config(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            assert manager.config_file == temp_json_config_file
            assert hasattr(manager, 'logger')
            assert hasattr(manager, 'scrapers')
            assert hasattr(manager, 'report')
            assert hasattr(manager, 'config')
            assert len(manager.scrapers) == 2
            assert "test_scraper_1" in manager.scrapers
            assert "test_scraper_2" in manager.scrapers

    def test_init_with_yaml_config(self, temp_yaml_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_yaml_config_file)

            assert manager.config_file == temp_yaml_config_file
            assert len(manager.scrapers) == 1
            assert "yaml_scraper" in manager.scrapers

    def test_load_config_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            ScraperManager("non_existent_file.json")

    def test_load_config_invalid_format(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid content")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported configuration file format"):
                ScraperManager(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_config_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                ScraperManager(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_config_scraper_creation_failure(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_factory.side_effect = Exception("Scraper creation failed")

            manager = ScraperManager(temp_json_config_file)

            assert len(manager.scrapers) == 0

    def test_load_config_no_scrapers_section(self):
        config = {"other_section": {"key": "value"}}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name

        try:
            manager = ScraperManager(temp_file)
            assert len(manager.scrapers) == 0
        finally:
            os.unlink(temp_file)

    def test_get_game_from_category(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            assert manager.get_game_from_category("store1", "magic") == "magic"
            assert manager.get_game_from_category("store1", "yugioh") == "yugioh"
            assert manager.get_game_from_category("store1", "pokemon") == "pokemon"
            assert manager.get_game_from_category("store1", "pokemon_singles") == "pokemon"

            assert manager.get_game_from_category("magic", "unknown") == "magic"
            assert manager.get_game_from_category("yugioh", "unknown") == "yugioh"

            assert manager.get_game_from_category("unknown", "unknown") == "otros"

    def test_save_results_per_category(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            results = {
                "magic": [{"name": "Lightning Bolt", "price": 100}],
                "pokemon": [{"name": "Pikachu", "price": 200}]
            }

            with patch('os.makedirs') as mock_makedirs, \
                    patch('builtins.open', new_callable=mock_open) as mock_file_open:

                manager.save_results_per_category("test_store", results)

                expected_calls = [
                    call("data/magic/magic", exist_ok=True),
                    call("data/pokemon/pokemon", exist_ok=True)
                ]
                mock_makedirs.assert_has_calls(expected_calls, any_order=True)
                assert mock_file_open.call_count == 2

    def test_run_scraper_success(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test_scraper", {})
            mock_results = {"magic": [{"name": "Card1", "price": 100}]}
            mock_report = {"magic": {"total_products": 1, "processed_products": 1}}

            mock_scraper.set_mock_results(mock_results)
            mock_scraper.set_mock_report(mock_report)
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            results = manager.run_scraper("test_scraper_1")

            assert results == mock_results
            assert mock_scraper.run_called
            assert mock_scraper.get_report_called
            assert manager.report["test_scraper_1"] == mock_report

    def test_run_scraper_not_found(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            results = manager.run_scraper("non_existent_scraper")

            assert results == {}

    def test_run_all_scrapers(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_results = {"magic": [{"name": "Card1", "price": 100}]}
            mock_report = {"magic": {"total_products": 1, "processed_products": 1}}

            mock_scraper.set_mock_results(mock_results)
            mock_scraper.set_mock_report(mock_report)
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            all_results = manager.run_all()

            assert len(all_results) == 2
            assert "test_scraper_1" in all_results
            assert "test_scraper_2" in all_results
            assert all_results["test_scraper_1"] == mock_results
            assert all_results["test_scraper_2"] == mock_results

    def test_run_all_scrapers_empty_config(self):
        config = {"scrapers": {}}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name

        try:
            manager = ScraperManager(temp_file)
            results = manager.run_all()

            assert results == {}
        finally:
            os.unlink(temp_file)

    def test_get_report(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            assert manager.get_report() == {}

            test_report = {"scraper1": {"total": 10, "processed": 8}}
            manager.report = test_report

            assert manager.get_report() == test_report

    def test_make_report(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            test_report = {
                "scraper1": {"total": 10, "processed": 8},
                "scraper2": {"total": 5, "processed": 5}
            }
            manager.report = test_report

            with patch('os.makedirs') as mock_makedirs, \
                    patch('builtins.open', new_callable=mock_open) as mock_file_open, \
                    patch('os.path.abspath') as mock_abspath, \
                    patch('os.path.dirname') as mock_dirname, \
                    patch('datetime.datetime') as mock_datetime:

                mock_dirname.return_value = "/fake/path"
                mock_abspath.side_effect = lambda x: f"/absolute{x}"
                mock_datetime.now.return_value.strftime.return_value = "20231201_123456"

                manager.make_report()

                mock_makedirs.assert_called_once_with("/absolute/fake/path/../../reports", exist_ok=True)
                expected_filename = "/absolute/fake/path/../../reports/scraper_report_20231201_123456.json"
                mock_file_open.assert_called_once_with(expected_filename, "w", encoding="utf-8")

    def test_integration_with_scraper_factory(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper1 = MockScraper("scraper1", {})
            mock_scraper2 = MockScraper("scraper2", {})
            mock_factory.side_effect = [mock_scraper1, mock_scraper2]

            manager = ScraperManager(temp_json_config_file)

            assert mock_factory.call_count == 2

            calls = mock_factory.call_args_list
            assert calls[0][0] == ("test_scraper_1", {"type": "guild_dreams", "base_url": "https://example1.com", "categories": {"magic": {"url": "https://example1.com/magic", "active": True}}})
            assert calls[1][0] == ("test_scraper_2", {"type": "card_universe", "base_url": "https://example2.com", "categories": {"pokemon": {"url": "https://example2.com/pokemon", "active": True}}})

    def test_logger_integration(self, temp_json_config_file):
        with patch('src.core.scraper_manager.LoggerFactory.create_logger') as mock_logger_factory:
            mock_logger = Mock()
            mock_logger_factory.return_value = mock_logger

            with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
                mock_scraper = MockScraper("test", {})
                mock_factory.return_value = mock_scraper

                manager = ScraperManager(temp_json_config_file)

                logger_calls = [call[0][0] for call in mock_logger_factory.call_args_list]
                assert "scraper_manager" in logger_calls
                assert manager.logger == mock_logger

    def test_error_handling_during_scraper_run(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})

            def failing_run():
                raise Exception("Scraper run failed")

            mock_scraper.run = failing_run
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            with pytest.raises(Exception, match="Scraper run failed"):
                manager.run_scraper("test_scraper_1")

    def test_config_access_after_loading(self, temp_json_config_file, sample_json_config):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            assert manager.config == sample_json_config
            assert manager.config["scrapers"]["test_scraper_1"]["type"] == "guild_dreams"

    def test_scraper_lifecycle(self, temp_json_config_file):
        with patch('src.core.scraper_manager.ScraperFactory.create_scraper') as mock_factory:
            mock_scraper = MockScraper("test", {})
            mock_results = {"magic": [{"name": "Card1", "price": 100}]}
            mock_report = {"magic": {"total_products": 1, "processed_products": 1}}

            mock_scraper.set_mock_results(mock_results)
            mock_scraper.set_mock_report(mock_report)
            mock_factory.return_value = mock_scraper

            manager = ScraperManager(temp_json_config_file)

            results = manager.run_all()

            report = manager.get_report()

            assert len(results) == 2
            assert len(report) == 2
            assert "test_scraper_1" in results
            assert "test_scraper_2" in results
            assert "test_scraper_1" in report
            assert "test_scraper_2" in report
