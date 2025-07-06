"""
Scraping stage for the pipeline
"""
from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage
from src.core.scraper_manager import ScraperManager


class ScrapingStage(BaseStage):
    """Stage for executing all scrapers"""
    
    @property
    def stage_name(self) -> str:
        return "Scraping"
    
    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Execute all scrapers"""
        try:
            self.logger.info("Starting scraping process...")
            config = context.get('config')
            manager = ScraperManager(config.config_path)
            results = manager.run_all()
            
            # Store manager for cleanup stage
            context['manager'] = manager
            context['scraper_results'] = results
            
            return PipelineResult(
                success=True,
                stage=PipelineStage.SCRAPING,
                data=results,
                message=f"Scraping completed. Found {len(results)} scrapers"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.SCRAPING,
                error=str(e)
            )
        
