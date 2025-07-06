"""
Cleanup stage for the pipeline
"""
from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage


class CleanupStage(BaseStage):
    """Stage for cleanup and final report generation"""

    @property
    def stage_name(self) -> str:
        return "Cleanup"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Cleanup resources and generate final report"""
        try:
            # Generate report if manager is available
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
