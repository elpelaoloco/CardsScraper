"""
Base classes for pipeline stages
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..models import PipelineResult, PipelineStage


class BaseStage(ABC):
    """Base class for all pipeline stages"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        """Execute the stage logic"""
        pass
    
    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Return the stage name for logging"""
        pass