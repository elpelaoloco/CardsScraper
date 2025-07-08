import pytest
import logging
from unittest.mock import Mock, patch, MagicMock

from src.pipeline.pipeline import ScraperPipeline
from src.pipeline.models import PipelineConfig, PipelineResult, PipelineStage
from src.pipeline.stages.base import BaseStage


class MockStage(BaseStage):
    def __init__(self, context, name, success=True, error_message=None, stage_enum=None, data=None):
        super().__init__(context)
        self._name = name
        self.success = success
        self.error_message = error_message
        self.stage_enum = stage_enum
        self.data = data
    
    @property
    def stage_name(self):
        return self._name
    
    def execute(self, context):
        if self.success:
            return PipelineResult(
                success=True,
                stage=self.stage_enum,
                message=f"{self._name} completed successfully",
                data=self.data
            )
        else:
            return PipelineResult(
                success=False,
                stage=self.stage_enum,
                error=self.error_message
            )


class TestScraperPipeline:
    
    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="configs/test_config.json",
            api_endpoint='https://api.test.com',
            output_dir="test_data"
        )
    
    def test_pipeline_initialization(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        
        assert pipeline.config == sample_config
        assert hasattr(pipeline, 'logger')
        assert hasattr(pipeline, 'context')
        assert pipeline.context['config'] == sample_config
        assert hasattr(pipeline, 'stages')
        assert len(pipeline.stages) == 6

    @patch('src.pipeline.pipeline.ScraperPipeline._initialize_stages')
    def test_run_success(self, mock_init_stages, sample_config):
        mock_stages = [
            MockStage(Mock(), "Init", success=True, stage_enum=PipelineStage.INIT),
            MockStage(Mock(), "Scraping", success=True, stage_enum=PipelineStage.SCRAPING),
            MockStage(Mock(), "Export", success=True, stage_enum=PipelineStage.EXPORT)
        ]
        mock_init_stages.return_value = mock_stages
        
        pipeline = ScraperPipeline(sample_config)
        summary = pipeline.run()
        
        assert summary['total_stages'] == 3
        assert summary['successful_stages'] == 3
        assert summary['failed_stages'] == 0

    @patch('src.pipeline.pipeline.ScraperPipeline._initialize_stages')
    def test_run_with_stage_failure(self, mock_init_stages, sample_config):
        mock_stages = [
            MockStage(Mock(), "Init", success=False, error_message="Permission denied", stage_enum=PipelineStage.INIT),
        ]
        mock_init_stages.return_value = mock_stages
        
        pipeline = ScraperPipeline(sample_config)
        summary = pipeline.run()
        
        assert summary['total_stages'] == 1
        assert summary['successful_stages'] == 0
        assert summary['failed_stages'] == 1
        
        init_detail = summary['stages_detail'][0]
        assert init_detail['stage'] == 'initialization'
        assert init_detail['success'] is False
        assert init_detail['error'] == "Permission denied"

    def test_generate_summary_with_context(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        
        pipeline.context.update({
            'consolidated_data': [
                {'name': 'Card1', 'store': 'store1'},
                {'name': 'Card2', 'store': 'store2'}
            ],
            'scraper_results': {
                'store1': {'magic': []},
                'store2': {'pokemon': []}
            },
            'report': {
                'store1': {'magic': {'total_products': 5, 'processed_products': 3}},
                'store2': {'pokemon': {'total_products': 2, 'processed_products': 2}}
            },
            'scraping_time': 15.5
        })
        
        pipeline_results = [
            PipelineResult(success=True, stage=PipelineStage.INIT, message="Init done"),
            PipelineResult(success=True, stage=PipelineStage.SCRAPING, message="Scraping done"),
            PipelineResult(success=False, stage=PipelineStage.EXPORT, error="Export failed")
        ]
        
        summary = pipeline._generate_summary(pipeline_results)
        
        assert summary['total_stages'] == 3
        assert summary['successful_stages'] == 2
        assert summary['failed_stages'] == 1
        assert summary['total_items_processed'] == 2
        assert summary['scrapers_executed'] == 2
        assert summary['scraping_time'] == 15.5
        
        assert len(summary['detailed_reports']) == 2
        store1_report = next(r for r in summary['detailed_reports'] if r['scraper'] == 'store1')
        assert store1_report['game'] == 'magic'
        assert store1_report['report']['total_products'] == 5

    def test_context_management(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        
        assert 'config' in pipeline.context
        assert pipeline.context['config'] == sample_config
        
        pipeline.context['test_data'] = "test_value"
        assert pipeline.context['test_data'] == "test_value"

    def test_stages_initialization(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        
        expected_stage_types = [
            'InitializationStage',
            'ScrapingStage', 
            'ConsolidationStage',
            'ExportStage',
            'PostRequestStage',
            'CleanupStage'
        ]
        
        actual_stage_types = [type(stage).__name__ for stage in pipeline.stages]
        assert actual_stage_types == expected_stage_types

    def test_pipeline_config_immutability(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        original_config = pipeline.config
        
        assert pipeline.config is original_config