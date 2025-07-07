
import requests
import pandas as pd
from typing import Any, Dict
import json
from .base import BaseStage
from ..models import PipelineResult, PipelineStage


class PostRequestStage(BaseStage):


    @property
    def stage_name(self) -> str:
        return "POST Request"

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Send consolidated results via POST request"""
        config = context.get('config')

        if not config.api_endpoint:
            return PipelineResult(
                success=True,
                stage=PipelineStage.POST_REQUEST,
                message="No API endpoint configured, skipping POST request"
            )

        try:
            self.logger.info(f"Sending POST request to {config.api_endpoint}")

            consolidated_data = context.get('consolidated_data', [])
            results = context.get('scraper_results', {})
            print(len(consolidated_data), len(results))

            payload = consolidated_data

            response = requests.post(
                config.api_endpoint,
                json=payload,
                headers=config.api_headers or {"Content-Type": "application/json"},
                timeout=config.request_timeout
            )

            if response.status_code == 200:
                return PipelineResult(
                    success=True,
                    stage=PipelineStage.POST_REQUEST,
                    message=f"POST request successful: {response.status_code}"
                )
            else:
                return PipelineResult(
                    success=False,
                    stage=PipelineStage.POST_REQUEST,
                    error=f"POST request failed: {response.status_code} - {response.text}"
                )

        except requests.exceptions.RequestException as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.POST_REQUEST,
                error=f"Request error: {str(e)}"
            )
        except Exception as e:
            return PipelineResult(
                success=False,
                stage=PipelineStage.POST_REQUEST,
                error=f"Unexpected error: {str(e)}"
            )
