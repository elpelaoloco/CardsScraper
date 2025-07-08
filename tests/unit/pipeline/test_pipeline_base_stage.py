import pytest
import logging
from unittest.mock import Mock
from typing import Any, Dict

from src.pipeline.stages.base import BaseStage
from src.pipeline.models import PipelineResult, PipelineStage


class ConcreteStage(BaseStage):

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self._stage_name = "TestStage"
        self._should_succeed = True
        self._return_data = None
        self._exception_to_raise = None

    @property
    def stage_name(self) -> str:
        return self._stage_name

    def execute(self, context: Dict[str, Any]) -> PipelineResult:
        if self._exception_to_raise:
            raise self._exception_to_raise

        if self._should_succeed:
            return PipelineResult(
                success=True,
                stage=PipelineStage.INIT,
                data=self._return_data,
                message="Test stage executed successfully"
            )
        else:
            return PipelineResult(
                success=False,
                stage=PipelineStage.INIT,
                error="Test stage failed"
            )

    def set_behavior(self, should_succeed=True, return_data=None, exception=None, stage_name=None):
        self._should_succeed = should_succeed
        self._return_data = return_data
        self._exception_to_raise = exception
        if stage_name:
            self._stage_name = stage_name


class TestBaseStage:

    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def concrete_stage(self, mock_logger):
        return ConcreteStage(mock_logger)

    def test_base_stage_init(self, mock_logger):
        stage = ConcreteStage(mock_logger)

        assert stage.logger == mock_logger
        assert hasattr(stage, 'execute')
        assert hasattr(stage, 'stage_name')

    def test_stage_name_property(self, concrete_stage):
        assert concrete_stage.stage_name == "TestStage"

        concrete_stage.set_behavior(stage_name="ModifiedStage")
        assert concrete_stage.stage_name == "ModifiedStage"

    def test_execute_success(self, concrete_stage):
        context = {"config": {"test": "data"}}
        test_data = {"result": "success"}

        concrete_stage.set_behavior(should_succeed=True, return_data=test_data)

        result = concrete_stage.execute(context)

        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.stage == PipelineStage.INIT
        assert result.data == test_data
        assert result.message == "Test stage executed successfully"
        assert result.error is None

    def test_execute_failure(self, concrete_stage):
        context = {"config": {"test": "data"}}

        concrete_stage.set_behavior(should_succeed=False)

        result = concrete_stage.execute(context)

        assert isinstance(result, PipelineResult)
        assert result.success is False
        assert result.stage == PipelineStage.INIT
        assert result.error == "Test stage failed"
        assert result.data is None
        assert result.message is None

    def test_execute_with_exception(self, concrete_stage):
        context = {"config": {"test": "data"}}
        test_exception = ValueError("Test exception")

        concrete_stage.set_behavior(exception=test_exception)

        with pytest.raises(ValueError, match="Test exception"):
            concrete_stage.execute(context)

    def test_execute_with_empty_context(self, concrete_stage):
        context = {}

        result = concrete_stage.execute(context)

        assert result.success is True

    def test_execute_with_none_context(self, concrete_stage):
        result = concrete_stage.execute(None)

        assert result.success is True

    def test_execute_with_complex_data(self, concrete_stage):
        context = {"config": {"test": "data"}}
        complex_data = {
            "scraped_items": [
                {"name": "Product 1", "price": 100},
                {"name": "Product 2", "price": 200}
            ],
            "metadata": {
                "timestamp": "2023-12-01T12:00:00",
                "scraper_count": 2
            },
            "stats": {
                "total_items": 2,
                "success_rate": 1.0
            }
        }

        concrete_stage.set_behavior(return_data=complex_data)

        result = concrete_stage.execute(context)

        assert result.success is True
        assert result.data == complex_data
        assert result.data["scraped_items"][0]["name"] == "Product 1"
        assert result.data["stats"]["total_items"] == 2

    def test_logger_usage(self, mock_logger):
        stage = ConcreteStage(mock_logger)

        assert stage.logger == mock_logger

        stage.logger.info("Test message")
        mock_logger.info.assert_called_once_with("Test message")

    def test_abstract_methods_enforcement(self):
        mock_logger = Mock(spec=logging.Logger)

        with pytest.raises(TypeError):
            BaseStage(mock_logger)

    def test_multiple_executions(self, concrete_stage):
        context1 = {"config": {"run": 1}}
        context2 = {"config": {"run": 2}}

        result1 = concrete_stage.execute(context1)
        assert result1.success is True

        result2 = concrete_stage.execute(context2)
        assert result2.success is True

        assert result1 is not result2
        assert result1.success == result2.success

    def test_stage_behavior_modification(self, concrete_stage):
        context = {"test": "data"}

        concrete_stage.set_behavior(should_succeed=True, return_data={"first": "run"})
        result1 = concrete_stage.execute(context)
        assert result1.success is True
        assert result1.data == {"first": "run"}

        concrete_stage.set_behavior(should_succeed=False)
        result2 = concrete_stage.execute(context)
        assert result2.success is False
        assert result2.error == "Test stage failed"

        concrete_stage.set_behavior(should_succeed=True, return_data={"third": "run"})
        result3 = concrete_stage.execute(context)
        assert result3.success is True
        assert result3.data == {"third": "run"}

    def test_stage_inheritance_structure(self, concrete_stage):
        assert isinstance(concrete_stage, BaseStage)
        assert hasattr(concrete_stage, 'logger')
        assert hasattr(concrete_stage, 'execute')
        assert hasattr(concrete_stage, 'stage_name')

        assert callable(concrete_stage.execute)
        assert isinstance(concrete_stage.stage_name, str)
