"""
Main pipeline orchestrator
"""
import logging
from typing import Dict, Any, List, Type
from .models import PipelineConfig, PipelineResult, PipelineStage
from ..core.logger_factory import LoggerFactory
from .stages import (
    InitializationStage,
    ScrapingStage,
    ConsolidationStage,
    ExportStage,
    PostRequestStage,
    CleanupStage
)
from .stages.base import BaseStage


class ScraperPipeline:
    """
    A pipeline for web scraping that processes data through multiple stages
    and sends results via POST request.
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = LoggerFactory.create_logger("ScraperPipeline")
        self.context = {'config': config}
        self.stages = self._initialize_stages()
        
    def _initialize_stages(self) -> List[BaseStage]:
        """Initialize all pipeline stages"""
        stage_classes = [
            InitializationStage,
            ScrapingStage,
            ConsolidationStage,
            ExportStage,
            PostRequestStage,
            CleanupStage
        ]
        
        return [stage_class(self.logger) for stage_class in stage_classes]
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the complete pipeline
        
        Returns:
            Dict containing pipeline execution results
        """
        pipeline_results = []
        
        for stage in self.stages:
            self.logger.info(f"Executing stage: {stage.stage_name}")
            result = stage.execute(self.context)
            pipeline_results.append(result)
            
            if result.success:
                self.logger.info(f"✓ {stage.stage_name}: {result.message}")
            else:
                self.logger.error(f"✗ {stage.stage_name}: {result.error}")
                # Continue with next stage even if current fails (except for critical stages)
                if result.stage in [PipelineStage.INIT, PipelineStage.SCRAPING]:
                    break
        
        return self._generate_summary(pipeline_results)
    
    def _generate_summary(self, pipeline_results: List[PipelineResult]) -> Dict[str, Any]:
        """Generate final pipeline execution summary"""
        successful_stages = [r for r in pipeline_results if r.success]
        failed_stages = [r for r in pipeline_results if not r.success]
        
        consolidated_data = self.context.get('consolidated_data', [])
        scraper_results = self.context.get('scraper_results', {})
        
        summary = {
            "total_stages": len(pipeline_results),
            "successful_stages": len(successful_stages),
            "failed_stages": len(failed_stages),
            "total_items_processed": len(consolidated_data),
            "scrapers_executed": len(scraper_results),
            "stages_detail": [
                {
                    "stage": r.stage.value,
                    "success": r.success,
                    "message": r.message,
                    "error": r.error
                }
                for r in pipeline_results
            ]
        }
        
        self.logger.info(f"Pipeline execution completed: {len(successful_stages)}/{len(pipeline_results)} stages successful")
        return summary
