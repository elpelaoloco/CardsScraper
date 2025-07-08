import pytest
import os
import json
import logging
import pandas as pd
import requests
from unittest.mock import Mock, patch, mock_open, MagicMock
from typing import Any, Dict

from src.pipeline.models import PipelineResult, PipelineStage, PipelineConfig
from src.pipeline.stages.initialization import InitializationStage
from src.pipeline.stages.scraping import ScrapingStage
from src.pipeline.stages.consolidation import ConsolidationStage
from src.pipeline.stages.export import ExportStage
from src.pipeline.stages.post_request import PostRequestStage
from src.pipeline.stages.cleanup import CleanupStage


class TestInitializationStage:
    
    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)
    
    @pytest.fixture
    def init_stage(self, mock_logger):
        return InitializationStage(mock_logger)
    
    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="test/config.json",
            output_dir="test_output"
        )
    
    @patch('os.makedirs')
    def test_stage_name(self, mock_makedirs, init_stage, sample_config):
        context = {'config': sample_config}
        
        result = init_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.INIT
        assert result.message == "Directories created successfully"
        assert result.error is None
        
        mock_makedirs.assert_called_once_with("test_output", exist_ok=True)
        init_stage.logger.info.assert_called_once_with("Created output directory: test_output")
    
    @patch('os.makedirs')
    def test_execute_makedirs_exception(self, mock_makedirs, init_stage, sample_config):
        context = {}
        
        result = init_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.INIT
        assert "AttributeError" in result.error or "'NoneType'" in result.error
    
    def test_execute_config_none(self, init_stage):
        context = {'config': None}
        
        result = init_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.INIT
        assert "AttributeError" in result.error or "'NoneType'" in result.error
    
    @patch('src.pipeline.stages.scraping.ScraperManager')
    def test_execute_scraper_manager_exception(self, mock_scraper_manager_class, scraping_stage, sample_config):
        mock_perf_counter.side_effect = [1000.0, 1005.5]
        
        mock_manager = Mock()
        mock_manager.run_all.side_effect = Exception("Scraping failed")
        mock_scraper_manager_class.return_value = mock_manager
        
        context = {'config': sample_config}
        
        result = scraping_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.SCRAPING
        assert result.error == "Scraping failed"
    
    def test_stage_name(self, scraping_stage):
        assert consolidation_stage.stage_name == "Consolidation"
    
    def test_execute_success(self, consolidation_stage):
        context = {'scraper_results': {}}
        
        result = consolidation_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.CONSOLIDATION
        assert result.message == "Consolidated 0 items"
        assert result.data == []
        assert context['consolidated_data'] == []
    
    def test_execute_empty_categories(self, consolidation_stage):
        context = {}
        
        result = consolidation_stage.execute(context)
        
        assert result.success is True
        assert result.message == "Consolidated 0 items"
        assert result.data == []
    
    def test_execute_exception(self, consolidation_stage):
        assert export_stage.stage_name == "Export"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.DataFrame.to_excel')
    @patch('os.path.join')
    def test_execute_success_with_data(self, mock_path_join, mock_to_excel, mock_file_open, export_stage, sample_config):
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        
        scraper_results = {}
        consolidated_data = []
        
        context = {
            'config': sample_config,
            'scraper_results': scraper_results,
            'consolidated_data': consolidated_data
        }
        
        result = export_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.EXPORT
        
        mock_to_excel.assert_called_once_with("test_output/test_data.xlsx", index=False)
        export_stage.logger.warning.assert_called_once_with("No data found to export. Creating empty Excel file.")
    
    @patch('builtins.open')
    def test_execute_save_json_exception(self, mock_file_open, export_stage, sample_config):
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        mock_to_excel.side_effect = Exception("Excel write failed")
        
        context = {
            'config': sample_config,
            'scraper_results': {},
            'consolidated_data': [{'name': 'test'}]
        }
        
        result = export_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.EXPORT
        assert "Excel write failed" in result.error


class TestPostRequestStage:
    
    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)
    
    @pytest.fixture
    def post_request_stage(self, mock_logger):
        return PostRequestStage(mock_logger)
    
    @pytest.fixture
    def sample_config_with_api(self):
        return PipelineConfig(
            config_path="test/config.json",
            api_endpoint="https://api.example.com/data",
            api_headers={"Authorization": "Bearer token"},
            request_timeout=60
        )
    
    @pytest.fixture
    def sample_config_no_api(self):
        return PipelineConfig(
            config_path="test/config.json"
        )
    
    def test_stage_name(self, post_request_stage, sample_config_no_api):
        context = {'config': sample_config_no_api}
        
        result = post_request_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.POST_REQUEST
        assert result.message == "No API endpoint configured, skipping POST request"
    
    @patch('requests.post')
    def test_execute_success(self, mock_post, post_request_stage, sample_config_with_api):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid data format"
        mock_post.return_value = mock_response
        
        context = {
            'config': sample_config_with_api,
            'consolidated_data': [],
            'scraper_results': {}
        }
        
        result = post_request_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.POST_REQUEST
        assert "POST request failed: 400 - Bad Request: Invalid data format" in result.error
    
    @patch('requests.post')
    def test_execute_request_exception(self, mock_post, post_request_stage, sample_config_with_api):
        mock_post.side_effect = ValueError("Unexpected error")
        
        context = {
            'config': sample_config_with_api,
            'consolidated_data': [],
            'scraper_results': {}
        }
        
        result = post_request_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.POST_REQUEST
        assert "Unexpected error: Unexpected error" in result.error
    
    @patch('requests.post')
    def test_execute_default_headers(self, mock_post, post_request_stage, sample_config_with_api):
        context = {
            'config': sample_config_with_api,
            'consolidated_data': [],
            'scraper_results': {}
        }
        
        result = post_request_stage.execute(context)
        
        assert result is not None
    
    def test_execute_success_with_manager(self, cleanup_stage):
        context = {}
        
        result = cleanup_stage.execute(context)
        
        assert result.success is True
        assert result.stage == PipelineStage.CLEANUP
        assert result.message == "Cleanup completed successfully"
    
    def test_execute_manager_none(self, cleanup_stage):
        mock_manager = Mock()
        mock_manager.make_report.side_effect = Exception("Report generation failed")
        
        context = {'manager': mock_manager}
        
        result = cleanup_stage.execute(context)
        
        assert result.success is False
        assert result.stage == PipelineStage.CLEANUP
        assert result.error == "Report generation failed"
        assert result.message is None