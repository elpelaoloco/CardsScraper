from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage


class CleanupStage(BaseStage):
    

    @property
    def stage_name(self) -> str:
        return "Cleanup"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        
        try:
            
            manager = context.get('manager')
            if manager:
                manager.make_report()

            return PipelineResult(
                success=True,
                stage=PipelineStage.CLEANUP,
                message="Cleanup completed successfully"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.CLEANUP,
                error=str(e)
            )
