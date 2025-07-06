"""
Initialization stage for the pipeline
"""
import os
from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage


class InitializationStage(BaseStage):
    """Stage for initializing directories and resources"""

    @property
    def stage_name(self) -> str:
        return "Initialization"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Create necessary directories"""
        try:
            output_dir = context.get('config').output_dir
            os.makedirs(output_dir, exist_ok=True)

            self.logger.info(f"Created output directory: {output_dir}")

            return PipelineResult(
                success=True,
                stage=PipelineStage.INIT,
                message="Directories created successfully"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.INIT,
                error=str(e)
            )
