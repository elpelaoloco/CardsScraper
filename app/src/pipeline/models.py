from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


class PipelineStage(Enum):
    INIT = "initialization"
    SCRAPING = "scraping"
    CONSOLIDATION = "consolidation"
    EXPORT = "export"
    POST_REQUEST = "post_request"
    CLEANUP = "cleanup"


@dataclass
class PipelineResult:
    """Result container for pipeline execution"""
    success: bool
    stage: PipelineStage
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class PipelineConfig:
    """Configuration for the pipeline"""
    config_path: str
    api_endpoint: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    output_dir: str = "data"
    json_filename: str = "prod_result.json"
    excel_filename: str = "consolidated_results.xlsx"
    request_timeout: int = 30
