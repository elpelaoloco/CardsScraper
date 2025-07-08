import pytest
import os
import json
import logging
from unittest.mock import Mock, patch, mock_open

from src.pipeline.models import PipelineResult, PipelineStage, PipelineConfig
from src.pipeline.stages.initialization import InitializationStage
from src.pipeline.stages.scraping import ScrapingStage
from src.pipeline.stages.consolidation import ConsolidationStage
from src.pipeline.stages.export import ExportStage
from src.pipeline.stages.post_request import PostRequestStage
from src.pipeline.stages.cleanup import CleanupStage


class TestInitializationStage:
    
    @pytest.fixture
    def init_stage(self):
        logger = Mock(spec=logging.Logger)
        return InitializationStage(logger)
    
    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="test/config.json",
            output_dir="test_output"
        )
    
    @patch('os.makedirs')
    def test_execute_success(self, mock_makedirs, init_stage, sample_config):
        context = {'config': sample_config}
        
        result = init_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.INIT
        mock_makedirs.assert_called_once_with("test_output", exist_ok=True)
    
    def test_execute_no_config(self, init_stage):
        context = {'config': None}
        
        result = init_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.INIT


class TestScrapingStage:
    
    @pytest.fixture
    def scraping_stage(self):
        logger = Mock(spec=logging.Logger)
        return ScrapingStage(logger)
    
    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(config_path="configs/test_config.json")
    
    @patch('src.pipeline.stages.scraping.ScraperManager')
    @patch('time.perf_counter')
    def test_execute_success(self, mock_perf_counter, mock_scraper_manager_class, scraping_stage, sample_config):
        mock_perf_counter.side_effect = [1000.0, 1005.5]
        
        mock_manager = Mock()
        mock_manager.run_all.return_value = {'store1': {'magic': []}}
        mock_manager.get_report.return_value = {'store1': {'magic': {'total_products': 0}}}
        mock_scraper_manager_class.return_value = mock_manager
        
        context = {'config': sample_config}
        
        result = scraping_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.SCRAPING


class TestConsolidationStage:
    
    @pytest.fixture
    def consolidation_stage(self):
        logger = Mock(spec=logging.Logger)
        return ConsolidationStage(logger)
    
    def test_execute_success(self, consolidation_stage):
        context = {'scraper_results': {}}
        
        result = consolidation_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.CONSOLIDATION
        assert result.data == []


class TestExportStage:
    
    @pytest.fixture
    def export_stage(self):
        logger = Mock(spec=logging.Logger)
        return ExportStage(logger)
    
    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="test/config.json",
            output_dir="test_output"
        )
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('pandas.DataFrame.to_excel')
    def test_execute_success(self, mock_to_excel, mock_json_dump, mock_file_open, export_stage, sample_config):
        context = {
            'config': sample_config,
            'scraper_results': {},
            'consolidated_data': []
        }
        
        result = export_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.EXPORT


class TestPostRequestStage:
    
    @pytest.fixture
    def post_request_stage(self):
        logger = Mock(spec=logging.Logger)
        return PostRequestStage(logger)
    
    @pytest.fixture
    def config_no_api(self):
        return PipelineConfig(config_path="test/config.json")
    
    def test_execute_no_api(self, post_request_stage, config_no_api):
        context = {'config': config_no_api}
        
        result = post_request_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.POST_REQUEST
        assert "No API endpoint" in result.message


class TestCleanupStage:
    
    @pytest.fixture
    def cleanup_stage(self):
        logger = Mock(spec=logging.Logger)
        return CleanupStage(logger)
    
    def test_execute_success(self, cleanup_stage):
        context = {}
        
        result = cleanup_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.CLEANUP