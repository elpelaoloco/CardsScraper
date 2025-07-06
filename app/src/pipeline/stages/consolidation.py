"""
Consolidation stage for the pipeline
"""
from typing import Any, Dict, List
from .base import BaseStage
from ..models import PipelineResult, PipelineStage


class ConsolidationStage(BaseStage):
    """Stage for consolidating results from all scrapers"""
    
    @property
    def stage_name(self) -> str:
        return "Consolidation"
    
    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Consolidate results from all scrapers"""
        try:
            self.logger.info("Consolidating results...")
            results = context.get('scraper_results', {})
            all_rows = []
            
            for scraper_name, categories_dict in results.items():
                if not categories_dict:
                    continue
                    
                for category_name, products in categories_dict.items():
                    if not products:
                        continue
                        
                    for item in products:
                        item['store'] = scraper_name
                        item['category'] = category_name
                        all_rows.append(item)
            
            context['consolidated_data'] = all_rows
            
            return PipelineResult(
                success=True,
                stage=PipelineStage.CONSOLIDATION,
                data=all_rows,
                message=f"Consolidated {len(all_rows)} items"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.CONSOLIDATION,
                error=str(e)
            )

