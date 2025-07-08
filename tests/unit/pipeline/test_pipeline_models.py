import pytest
from src.pipeline.models import PipelineStage, PipelineResult, PipelineConfig


class TestPipelineStage:

    def test_pipeline_stage_enum_values(self):
        assert PipelineStage.INIT.value == "initialization"
        assert PipelineStage.SCRAPING.value == "scraping"
        assert PipelineStage.CONSOLIDATION.value == "consolidation"
        assert PipelineStage.EXPORT.value == "export"
        assert PipelineStage.POST_REQUEST.value == "post_request"
        assert PipelineStage.CLEANUP.value == "cleanup"

    def test_pipeline_stage_enum_count(self):
        stages = list(PipelineStage)
        assert len(stages) == 6

    def test_pipeline_stage_string_representation(self):
        assert str(PipelineStage.INIT) == "PipelineStage.INIT"
        assert str(PipelineStage.SCRAPING) == "PipelineStage.SCRAPING"


class TestPipelineResult:

    def test_pipeline_result_creation_success(self):
        result = PipelineResult(
            success=True,
            stage=PipelineStage.INIT,
            message="Initialization completed"
        )

        assert result.success is True
        assert result.stage == PipelineStage.INIT
        assert result.message == "Initialization completed"
        assert result.data is None
        assert result.error is None

    def test_pipeline_result_creation_failure(self):
        result = PipelineResult(
            success=False,
            stage=PipelineStage.SCRAPING,
            error="Scraping failed due to network error"
        )

        assert result.success is False
        assert result.stage == PipelineStage.SCRAPING
        assert result.error == "Scraping failed due to network error"
        assert result.data is None
        assert result.message is None

    def test_pipeline_result_with_data(self):
        test_data = {"scraped_items": 10, "stores": ["store1", "store2"]}

        result = PipelineResult(
            success=True,
            stage=PipelineStage.CONSOLIDATION,
            data=test_data,
            message="Consolidation successful"
        )

        assert result.success is True
        assert result.stage == PipelineStage.CONSOLIDATION
        assert result.data == test_data
        assert result.message == "Consolidation successful"
        assert result.error is None

    def test_pipeline_result_all_fields(self):
        test_data = [{"product": "test"}]

        result = PipelineResult(
            success=True,
            stage=PipelineStage.EXPORT,
            data=test_data,
            error="Minor warning",
            message="Export completed with warnings"
        )

        assert result.success is True
        assert result.stage == PipelineStage.EXPORT
        assert result.data == test_data
        assert result.error == "Minor warning"
        assert result.message == "Export completed with warnings"

    def test_pipeline_result_equality(self):
        result1 = PipelineResult(
            success=True,
            stage=PipelineStage.INIT,
            message="Test"
        )

        result2 = PipelineResult(
            success=True,
            stage=PipelineStage.INIT,
            message="Test"
        )

        result3 = PipelineResult(
            success=False,
            stage=PipelineStage.INIT,
            message="Test"
        )

        assert result1 == result2
        assert result1 != result3


class TestPipelineConfig:

    def test_pipeline_config_creation_minimal(self):
        config = PipelineConfig(config_path="test/config.json")

        assert config.config_path == "test/config.json"
        assert config.api_endpoint is None
        assert config.api_headers is None
        assert config.output_dir == "data"
        assert config.json_filename == "prod_result.json"
        assert config.excel_filename == "consolidated_results.xlsx"
        assert config.request_timeout == 30

    def test_pipeline_config_creation_full(self):
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}

        config = PipelineConfig(
            config_path="configs/prod_config.json",
            api_endpoint="https://api.example.com/data",
            api_headers=headers,
            output_dir="output",
            json_filename="results.json",
            excel_filename="data.xlsx",
            request_timeout=60
        )

        assert config.config_path == "configs/prod_config.json"
        assert config.api_endpoint == "https://api.example.com/data"
        assert config.api_headers == headers
        assert config.output_dir == "output"
        assert config.json_filename == "results.json"
        assert config.excel_filename == "data.xlsx"
        assert config.request_timeout == 60

    def test_pipeline_config_defaults(self):
        config = PipelineConfig(
            config_path="test.json",
            api_endpoint="https://api.test.com"
        )

        assert config.output_dir == "data"
        assert config.json_filename == "prod_result.json"
        assert config.excel_filename == "consolidated_results.xlsx"
        assert config.request_timeout == 30
        assert config.api_headers is None

    def test_pipeline_config_api_headers_empty_dict(self):
        config = PipelineConfig(
            config_path="test.json",
            api_headers={}
        )

        assert config.api_headers == {}

    def test_pipeline_config_modification(self):
        config = PipelineConfig(config_path="test.json")

        config.output_dir = "new_output"
        config.request_timeout = 120
        config.api_endpoint = "https://new-api.com"

        assert config.output_dir == "new_output"
        assert config.request_timeout == 120
        assert config.api_endpoint == "https://new-api.com"

    def test_pipeline_config_equality(self):
        config1 = PipelineConfig(
            config_path="test.json",
            output_dir="data",
            request_timeout=30
        )

        config2 = PipelineConfig(
            config_path="test.json",
            output_dir="data",
            request_timeout=30
        )

        config3 = PipelineConfig(
            config_path="test.json",
            output_dir="different",
            request_timeout=30
        )

        assert config1 == config2
        assert config1 != config3

    def test_pipeline_config_string_representation(self):
        config = PipelineConfig(
            config_path="test.json",
            api_endpoint="https://api.test.com"
        )

        config_str = str(config)
        assert "config_path='test.json'" in config_str
        assert "api_endpoint='https://api.test.com'" in config_str
