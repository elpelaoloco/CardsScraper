
import os
import pandas as pd
from typing import Any, Dict
from .base import BaseStage
from ..models import PipelineResult, PipelineStage
from src.utils.save_results import save_dict_as_json


class ExportStage(BaseStage):

    @property
    def stage_name(self) -> str:
        return "Export"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:

        try:
            self.logger.info("Exporting results...")

            config = context.get('config')
            results = context.get('scraper_results', {})
            consolidated_data = context.get('consolidated_data', [])

            json_file = os.path.join(config.output_dir, config.json_filename)
            save_dict_as_json(results, json_file)

            excel_file = os.path.join(config.output_dir, config.excel_filename)
            if not consolidated_data:
                self.logger.warning("No data found to export. Creating empty Excel file.")
                empty_df = pd.DataFrame(
                    columns=["name", "price", "url", "store", "category", "timestamp"]
                )
                empty_df.to_excel(excel_file, index=False)
            else:
                df = pd.DataFrame(consolidated_data)
                df.to_excel(excel_file, index=False)

            return PipelineResult(
                success=True,
                stage=PipelineStage.EXPORT,
                message=f"Results exported to {json_file} and {excel_file}"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.EXPORT,
                error=str(e)
            )
