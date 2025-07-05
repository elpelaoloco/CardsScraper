from typing import Dict, Any
from src.core.base_scraper import BaseScraper
from src.scrapers.guild_dreams import GuildDreamsScraper
from src.scrapers.card_universe import CardUniverseScraper
from src.scrapers.hunter_card_tcg import HunterCardTCG
from src.scrapers.third_impact import ThirdImpact
from src.scrapers.la_comarca import LaComarcaScraper
from src.scrapers.game_of_magic import GameOfMagicScraper
from src.scrapers.el_reino import ElReinoScraper
class ScraperFactory:
    @staticmethod
    def create_scraper(name: str, config: Dict[str, Any]) -> BaseScraper:
        site_type = config.get('type', '').lower()
        if site_type == 'guild_dreams':
            return GuildDreamsScraper(name, config)
        elif site_type == 'card_universe':
            return CardUniverseScraper(name, config)
        elif site_type == 'hunter_card_tcg':
            return HunterCardTCG(name, config)
        elif site_type == 'thirdimpact':
            return ThirdImpact(name, config)
        elif site_type == 'lacomarca':
            return LaComarcaScraper(name, config)
        elif site_type == 'game_of_magic':
            return GameOfMagicScraper(name, config)
        elif site_type == 'el_reino':
            return ElReinoScraper(name, config)
        else:
            raise ValueError(f"Unknown site type: {site_type}")

