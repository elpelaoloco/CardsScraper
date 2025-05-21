from typing import Dict, Any
from src.core.base_scraper import BaseScraper
from src.scrapers.guild_dreams import GuildDreamsScraper
class ScraperFactory:
    @staticmethod
    def create_scraper(name: str, config: Dict[str, Any]) -> BaseScraper:
        site_type = config.get('type', '').lower()
        
        if site_type == 'guild_dreams':
            return GuildDreamsScraper(name, config)
        else:
            raise ValueError(f"Unknown site type: {site_type}")

