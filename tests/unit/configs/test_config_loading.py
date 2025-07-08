import pytest
import json
import os
from unittest.mock import patch, mock_open

from src.core.scraper_manager import ScraperManager


class TestConfigLoading:

    @pytest.fixture
    def sample_config_content(self):
        return {
            "scrapers": {
                "test_store": {
                    "type": "test_scraper",
                    "headless": True,
                    "categories": {
                        "pokemon": {
                            "url": "https://test.com/pokemon",
                            "selectors": {
                                "product_selector": "div.product",
                                "urls_selector": "a.link",
                                "price_selector": ".price",
                                "title_selector": "h1"
                            }
                        }
                    }
                }
            }
        }

    def test_load_config_file_exists(self, sample_config_content):
        config_json = json.dumps(sample_config_content)

        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                manager = ScraperManager("test_config.json")

        assert hasattr(manager, 'config')
        assert 'test_store' in manager.config['scrapers']

    def test_load_config_file_not_exists(self):
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                ScraperManager("nonexistent_config.json")

    def test_load_config_invalid_json(self):
        invalid_json = '{"scrapers": {"incomplete": true'

        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with patch('os.path.exists', return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    ScraperManager("invalid_config.json")

    def test_load_config_empty_file(self):
        with patch('builtins.open', mock_open(read_data='')):
            with patch('os.path.exists', return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    ScraperManager("empty_config.json")

    def test_load_config_missing_scrapers_key(self):
        config_without_scrapers = '{"other_key": "value"}'

        with patch('builtins.open', mock_open(read_data=config_without_scrapers)):
            with patch('os.path.exists', return_value=True):
                manager = ScraperManager("config.json")

        assert manager.config == {"other_key": "value"}

    @patch('os.path.exists')
    def test_config_file_path_resolution(self, mock_exists):
        mock_exists.return_value = True
        config_json = '{"scrapers": {}}'

        with patch('builtins.open', mock_open(read_data=config_json)) as mock_file:
            ScraperManager("configs/test_config.json")

        mock_file.assert_called_once_with("configs/test_config.json", 'r')

    def test_config_unicode_handling(self):
        config_with_unicode = {
            "scrapers": {
                "tienda_española": {
                    "type": "test",
                    "categories": {
                        "pokémon": {
                            "url": "https://tienda.es/pokémon",
                            "selectors": {
                                "title_selector": "h1[title*='Pokémon']"
                            }
                        }
                    }
                }
            }
        }
        config_json = json.dumps(config_with_unicode, ensure_ascii=False)

        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                manager = ScraperManager("unicode_config.json")

        assert 'tienda_española' in manager.config['scrapers']
        assert 'pokémon' in manager.config['scrapers']['tienda_española']['categories']

    def test_config_nested_structure_access(self, sample_config_content):
        config_json = json.dumps(sample_config_content)

        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                manager = ScraperManager("test_config.json")

        scrapers = manager.config['scrapers']
        test_store = scrapers['test_store']
        pokemon_category = test_store['categories']['pokemon']
        selectors = pokemon_category['selectors']

        assert test_store['type'] == 'test_scraper'
        assert test_store['headless'] is True
        assert pokemon_category['url'] == 'https://test.com/pokemon'
        assert selectors['product_selector'] == 'div.product'

    def test_config_with_comments_handling(self):
        config_with_newlines = '''
        {
            "scrapers": {
                "test_store": {
                    "type": "test_scraper",
                    "headless": true
                }
            }
        }
        '''

        with patch('builtins.open', mock_open(read_data=config_with_newlines)):
            with patch('os.path.exists', return_value=True):
                manager = ScraperManager("formatted_config.json")

        assert 'test_store' in manager.config['scrapers']
        assert manager.config['scrapers']['test_store']['headless'] is True
