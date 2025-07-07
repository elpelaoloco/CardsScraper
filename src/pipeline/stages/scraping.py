"""
Scraping stage for the pipeline
"""
from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage
from src.core.scraper_manager import ScraperManager
from time import perf_counter


class ScrapingStage(BaseStage):

    @property
    def stage_name(self) -> str:
        return "Scraping"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        try:
            self.logger.info("Starting scraping process...")
            config = context.get('config')
            manager = ScraperManager(config.config_path)
            start = perf_counter()
            results = manager.run_all()
            end = perf_counter()
            report = manager.get_report()

            context['manager'] = manager
            context['scraper_results'] = results
            context['report'] = report
            context['scraping_time'] = end - start

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
