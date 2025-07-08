import pytest
import logging
from unittest.mock import Mock, patch, MagicMock

from src.pipeline.pipeline import ScraperPipeline
from src.pipeline.models import PipelineConfig, PipelineResult, PipelineStage
from src.pipeline.stages.base import BaseStage


class MockStage(BaseStage):
        pipeline = ScraperPipeline(sample_config)
        
        assert pipeline.config == sample_config
        assert hasattr(pipeline, 'logger')
        assert hasattr(pipeline, 'context')
        assert pipeline.context['config'] == sample_config
        assert hasattr(pipeline, 'stages')
        assert len(pipeline.stages) == 6  # All 6 stages
    
    def test_initialize_stages(self, pipeline):
        mock_stages = []
        stage_data = [
            ("Init", PipelineStage.INIT, None),
            ("Scraping", PipelineStage.SCRAPING, {"store1": {"magic": [{"name": "Card1"}]}}),
            ("Consolidation", PipelineStage.CONSOLIDATION, [{"name": "Card1", "store": "store1"}]),
            ("Export", PipelineStage.EXPORT, None),
            ("POST Request", PipelineStage.POST_REQUEST, None),
            ("Cleanup", PipelineStage.CLEANUP, None)
        ]
        
        for i, (name, stage_enum, data) in enumerate(stage_data):
            mock_stage = MockStage(Mock(), name, success=True, stage_enum=stage_enum, data=data)
            mock_stages.append(mock_stage)
        
        mock_init.return_value = mock_stages[0]
        mock_scraping.return_value = mock_stages[1]
        mock_consolidation.return_value = mock_stages[2]
        mock_export.return_value = mock_stages[3]
        mock_post.return_value = mock_stages[4]
        mock_cleanup.return_value = mock_stages[5]
        
        pipeline = ScraperPipeline(sample_config)
        summary = pipeline.run()
        
        assert summary['total_stages'] == 6
        assert summary['successful_stages'] == 6
        assert summary['failed_stages'] == 0
        assert 'stages_detail' in summary
        assert len(summary['stages_detail']) == 6
        
        for stage_detail in summary['stages_detail']:
            assert stage_detail['success'] is True
            assert stage_detail['error'] is None
    
    @patch('src.pipeline.stages.initialization.InitializationStage')
    @patch('src.pipeline.stages.scraping.ScrapingStage')
    @patch('src.pipeline.stages.consolidation.ConsolidationStage')
    @patch('src.pipeline.stages.export.ExportStage')
    @patch('src.pipeline.stages.post_request.PostRequestStage')
    @patch('src.pipeline.stages.cleanup.CleanupStage')
    def test_run_with_stage_failure(self, mock_cleanup, mock_post, mock_export, 
                                   mock_consolidation, mock_scraping, mock_init, sample_config):
        mock_stages = [
            MockStage(Mock(), "Init", success=False, error_message="Permission denied", stage_enum=PipelineStage.INIT),
        ]
        
        mock_init.return_value = mock_stages[0]
        
        pipeline = ScraperPipeline(sample_config)
        summary = pipeline.run()
        
        assert summary['total_stages'] == 1
        assert summary['successful_stages'] == 0
        assert summary['failed_stages'] == 1
        
        init_detail = summary['stages_detail'][0]
        assert init_detail['stage'] == 'initialization'
        assert init_detail['success'] is False
        assert init_detail['error'] == "Permission denied"
    
    @patch('src.pipeline.stages.initialization.InitializationStage')
    @patch('src.pipeline.stages.scraping.ScrapingStage')
    @patch('src.pipeline.stages.consolidation.ConsolidationStage')
    @patch('src.pipeline.stages.export.ExportStage')
    @patch('src.pipeline.stages.post_request.PostRequestStage')
    @patch('src.pipeline.stages.cleanup.CleanupStage')
    def test_run_with_non_critical_failure(self, mock_cleanup, mock_post, mock_export,
                                          mock_consolidation, mock_scraping, mock_init, sample_config):
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
    
    def test_generate_summary_minimal_data(self, sample_config):
        pipeline = ScraperPipeline(sample_config)
        
        assert 'config' in pipeline.context
        assert pipeline.context['config'] == sample_config
        
        pipeline.context['test_data'] = "test_value"
        assert pipeline.context['test_data'] == "test_value"
    
    def test_logger_creation(self, sample_config):
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
    
    def test_pipeline_immutable_config(self, sample_config):
