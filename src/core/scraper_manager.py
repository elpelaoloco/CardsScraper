import json
import yaml
from typing import Dict, Any, List
from src.core.scraper_factory import ScraperFactory
from src.core.logger_factory import LoggerFactory
import os
import datetime
class ScraperManager:
    def __init__(self, config_file: str):
        self.logger = LoggerFactory.create_logger("scraper_manager")
        self.config_file = config_file
        self.scrapers = {}
        self.report = {}
        self.load_config()
    
    def load_config(self) -> None:
        try:
            self.logger.info(f"Loading configuration from {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.json'):
                    config = json.load(f)
                elif self.config_file.endswith(('.yaml', '.yml')):
                    config = yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported configuration file format")
            
            self.config = config
            
            for name, scraper_config in config.get('scrapers', {}).items():
                try:
                    self.logger.info(f"Creating scraper for {name}")
                    self.scrapers[name] = ScraperFactory.create_scraper(name, scraper_config)
                    self.logger.info(f"Created scraper: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to create scraper {name}: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}", exc_info=True)
            raise
    
    def run_scraper(self, name: str) -> List[Dict[str, Any]]:

        if name not in self.scrapers:
            self.logger.error(f"Scraper not found: {name}")
            return []
        
        self.logger.info(f"Running scraper: {name}")
        results = self.scrapers[name].run()
        self.report[name] = self.scrapers[name].get_report()


        
        for category_name in results.keys():
            self.scrapers[name].save_results(category_name)
        

        self.scrapers[name].save_results()
        
        return results
    
    def run_all(self) -> Dict[str, List[Dict[str, Any]]]:

        self.logger.info("Running all scrapers")
        results = {}
        
        for name, scraper in self.scrapers.items():
            results[name] = self.run_scraper(name)
        
        return results
    
    def make_report(self) -> None:
        self.logger.info("Generating report")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        report_dir = os.path.join(target_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        file_name= f"scraper_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(report_dir, file_name)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        self.logger.info(f"Report saved to {report_path}")
        pass
