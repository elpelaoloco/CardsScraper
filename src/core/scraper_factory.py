from typing import Dict, Any
from src.core.base_scraper import BaseScraper
from src.scrapers.guild_dreams import GuildDreamsScraper
from src.scrapers.card_universe import CardUniverseScraper
from src.scrapers.hunter_card_tcg import HunterCardTCG
from src.scrapers.third_impact import ThirdImpact
class ScraperFactory:
    @staticmethod
    def create_scraper(name: str, config: Dict[str, Any]) -> BaseScraper:
        site_type = config.get('type', '').lower()
        if site_type == 'guild_dreams':
            return GuildDreamsScraper(name, config)
        elif site_type == 'card_universe':
            return CardUniverseScraper(name, config)
        elif site_type == 'huntercardtcg':
            return HunterCardTCG(name, config)
        elif site_type == 'thirdimpact':
            return ThirdImpact(name, config)
        else:
            raise ValueError(f"Unknown site type: {site_type}")

