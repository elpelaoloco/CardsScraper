import pytest
import json
import os

from src.core.scraper_manager import ScraperManager


class TestRealConfigs:
    
    @pytest.fixture(scope="class")
    def config_dir(self):
        return "configs"
    
    @pytest.fixture(scope="class")
    def config_files(self, config_dir):
        return [
            "test_config.json",
            "prod_config.json", 
            "scrapers_config.json"
        ]
    
    def test_config_files_exist(self, config_dir, config_files):
        for config_file in config_files:
            config_path = os.path.join(config_dir, config_file)
            assert os.path.exists(config_path), f"Config file {config_file} not found"
    
    def test_config_files_valid_json(self, config_dir, config_files):
        for config_file in config_files:
            config_path = os.path.join(config_dir, config_file)
            
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {config_file}: {e}")
    
    def test_test_config_structure(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert "scrapers" in config
        assert isinstance(config["scrapers"], dict)
        assert len(config["scrapers"]) > 0
    
    def test_test_config_scrapers_have_required_fields(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for scraper_name, scraper_config in config["scrapers"].items():
            assert "type" in scraper_config, f"Scraper {scraper_name} missing 'type'"
            assert "categories" in scraper_config, f"Scraper {scraper_name} missing 'categories'"
            
            for category_name, category_config in scraper_config["categories"].items():
                assert "url" in category_config, f"Category {category_name} in {scraper_name} missing 'url'"
                assert "selectors" in category_config, f"Category {category_name} in {scraper_name} missing 'selectors'"
    
    def test_test_config_urls_format(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for scraper_name, scraper_config in config["scrapers"].items():
            for category_name, category_config in scraper_config["categories"].items():
                url = category_config["url"]
                assert url.startswith("http"), f"Invalid URL format in {scraper_name}.{category_name}: {url}"
                assert "://" in url, f"Invalid URL format in {scraper_name}.{category_name}: {url}"
    
    def test_test_config_selectors_present(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_selectors = ["product_selector", "urls_selector"]
        
        for scraper_name, scraper_config in config["scrapers"].items():
            for category_name, category_config in scraper_config["categories"].items():
                selectors = category_config["selectors"]
                
                for required_selector in required_selectors:
                    assert required_selector in selectors, f"Missing {required_selector} in {scraper_name}.{category_name}"
    
    def test_scrapers_config_structure(self, config_dir):
        config_path = os.path.join(config_dir, "scrapers_config.json")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            assert isinstance(config, dict)
    
    def test_config_can_be_loaded_by_scraper_manager(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        try:
            manager = ScraperManager(config_path)
            assert hasattr(manager, 'config')
            assert len(manager.config.get('scrapers', {})) > 0
        except Exception as e:
            pytest.fail(f"ScraperManager failed to load test config: {e}")
    
    def test_config_stores_count(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        scrapers_count = len(config["scrapers"])
        assert scrapers_count >= 3, f"Expected at least 3 scrapers, found {scrapers_count}"
    
    def test_config_categories_coverage(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        all_categories = set()
        for scraper_config in config["scrapers"].values():
            all_categories.update(scraper_config["categories"].keys())
        
        expected_categories = {"pokemon", "magic", "yugioh"}
        found_categories = all_categories.intersection(expected_categories)
        
        assert len(found_categories) >= 2, f"Expected at least 2 game categories, found: {found_categories}"
    
    def test_config_store_types_unique(self, config_dir):
        config_path = os.path.join(config_dir, "test_config.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        store_types = []
        for scraper_config in config["scrapers"].values():
            store_types.append(scraper_config["type"])
        
        unique_types = set(store_types)
        assert len(unique_types) == len(store_types), f"Duplicate store types found: {store_types}"