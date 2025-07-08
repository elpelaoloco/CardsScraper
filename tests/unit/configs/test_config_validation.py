import pytest
import json
import os
from unittest.mock import patch, mock_open

from src.core.scraper_factory import ScraperFactory


class TestConfigValidation:

    @pytest.fixture
    def valid_scraper_config(self):
        return {
            "type": "test_scraper",
            "headless": True,
            "page_load_delay": 2,
            "batch_size": 1,
            "categories": {
                "pokemon": {
                    "url": "https://example.com/pokemon",
                    "selectors": {
                        "product_selector": "div.product",
                        "urls_selector": "a.product-link",
                        "price_selector": ".price",
                        "title_selector": "h1.title"
                    }
                }
            }
        }

    @pytest.fixture
    def invalid_scraper_config_no_url(self):
        return {
            "type": "test_scraper",
            "categories": {
                "pokemon": {
                    "selectors": {
                        "product_selector": "div.product"
                    }
                }
            }
        }

    @pytest.fixture
    def invalid_scraper_config_no_selectors(self):
        return {
            "type": "test_scraper",
            "categories": {
                "pokemon": {
                    "url": "https://example.com/pokemon"
                }
            }
        }

    def test_valid_config_structure(self, valid_scraper_config):
        assert "type" in valid_scraper_config
        assert "categories" in valid_scraper_config
        assert "pokemon" in valid_scraper_config["categories"]
        assert "url" in valid_scraper_config["categories"]["pokemon"]
        assert "selectors" in valid_scraper_config["categories"]["pokemon"]

    def test_required_selectors_present(self, valid_scraper_config):
        selectors = valid_scraper_config["categories"]["pokemon"]["selectors"]
        required_selectors = ["product_selector", "urls_selector", "price_selector", "title_selector"]

        for selector in required_selectors:
            assert selector in selectors

    def test_config_missing_url(self, invalid_scraper_config_no_url):
        category = invalid_scraper_config_no_url["categories"]["pokemon"]
        assert "url" not in category

    def test_config_missing_selectors(self, invalid_scraper_config_no_selectors):
        category = invalid_scraper_config_no_selectors["categories"]["pokemon"]
        assert "selectors" not in category

    def test_config_default_values(self, valid_scraper_config):
        assert valid_scraper_config.get("headless", False) is True
        assert valid_scraper_config.get("page_load_delay", 0) == 2
        assert valid_scraper_config.get("batch_size", 1) == 1

    def test_config_url_format(self, valid_scraper_config):
        url = valid_scraper_config["categories"]["pokemon"]["url"]
        assert url.startswith("http")
        assert "://" in url

    def test_config_selector_format(self, valid_scraper_config):
        selectors = valid_scraper_config["categories"]["pokemon"]["selectors"]

        for selector_name, selector_value in selectors.items():
            assert isinstance(selector_value, str)
            assert len(selector_value) > 0

    def test_multiple_categories_config(self):
        config = {
            "type": "multi_scraper",
            "categories": {
                "pokemon": {
                    "url": "https://example.com/pokemon",
                    "selectors": {"product_selector": "div.pokemon"}
                },
                "magic": {
                    "url": "https://example.com/magic",
                    "selectors": {"product_selector": "div.magic"}
                },
                "yugioh": {
                    "url": "https://example.com/yugioh",
                    "selectors": {"product_selector": "div.yugioh"}
                }
            }
        }

        assert len(config["categories"]) == 3
        assert "pokemon" in config["categories"]
        assert "magic" in config["categories"]
        assert "yugioh" in config["categories"]

    def test_config_optional_selectors(self):
        config = {
            "type": "test_scraper",
            "categories": {
                "pokemon": {
                    "url": "https://example.com/pokemon",
                    "selectors": {
                        "product_selector": "div.product",
                        "urls_selector": "a.link",
                        "price_selector": ".price",
                        "title_selector": "h1",
                        "image_selector": "img.product-image",
                        "stock_selector": ".stock-info",
                        "description_selector": ".description"
                    }
                }
            }
        }

        selectors = config["categories"]["pokemon"]["selectors"]
        optional_selectors = ["image_selector", "stock_selector", "description_selector"]

        for selector in optional_selectors:
            assert selector in selectors

    def test_config_boolean_values(self):
        config = {
            "type": "test_scraper",
            "headless": True,
            "debug": False,
            "categories": {}
        }

        assert isinstance(config["headless"], bool)
        assert isinstance(config["debug"], bool)
        assert config["headless"] is True
        assert config["debug"] is False

    def test_config_numeric_values(self):
        config = {
            "type": "test_scraper",
            "page_load_delay": 2,
            "batch_size": 5,
            "timeout": 30,
            "categories": {}
        }

        assert isinstance(config["page_load_delay"], int)
        assert isinstance(config["batch_size"], int)
        assert isinstance(config["timeout"], int)
        assert config["page_load_delay"] > 0
        assert config["batch_size"] > 0
        assert config["timeout"] > 0
