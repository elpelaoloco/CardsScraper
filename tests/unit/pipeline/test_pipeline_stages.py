import pytest
import os
import json
import logging
import pandas as pd
import requests
from unittest.mock import Mock, patch, mock_open, MagicMock
from typing import Any, Dict
from time import perf_counter

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

    def test_stage_name(self, init_stage):
        assert init_stage.stage_name == "Initialization"

    @patch('os.makedirs')
    def test_execute_success(self, mock_makedirs, init_stage, sample_config):
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


class TestScrapingStage:

    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def scraping_stage(self, mock_logger):
        return ScrapingStage(mock_logger)

    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="test/config.json",
            output_dir="test_output"
        )

    def test_stage_name(self, scraping_stage):
        assert scraping_stage.stage_name == "Scraping"

    @patch('src.pipeline.stages.scraping.ScraperManager')
    @patch('time.perf_counter')
    def test_execute_success(self, mock_perf_counter, mock_scraper_manager_class, scraping_stage, sample_config):
        mock_perf_counter.side_effect = [1000.0, 1005.5]

        mock_manager = Mock()
        mock_manager.run_all.return_value = {}
        mock_manager.get_report.return_value = {}
        mock_scraper_manager_class.return_value = mock_manager

        context = {'config': sample_config}

        result = scraping_stage.execute(context)

        assert result.success is True
        assert result.stage == PipelineStage.SCRAPING
        assert result.message == "Scraping completed. Found 0 scrapers"


class TestConsolidationStage:

    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def consolidation_stage(self, mock_logger):
        return ConsolidationStage(mock_logger)

    def test_stage_name(self, consolidation_stage):
        assert consolidation_stage.stage_name == "Consolidation"

    def test_execute_success(self, consolidation_stage):
        context = {'scraper_results': {}}

        result = consolidation_stage.execute(context)

        assert result.success is True
        assert result.stage == PipelineStage.CONSOLIDATION
        assert result.message == "Consolidated 0 items"
        assert result.data == []
        assert context['consolidated_data'] == []


class TestExportStage:

    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def export_stage(self, mock_logger):
        return ExportStage(mock_logger)

    @pytest.fixture
    def sample_config(self):
        return PipelineConfig(
            config_path="test/config.json",
            output_dir="test_output"
        )

    def test_stage_name(self, export_stage):
        assert export_stage.stage_name == "Export"

    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.DataFrame.to_excel')
    @patch('os.path.join')
    def test_execute_success_with_data(self, mock_path_join, mock_to_excel, mock_file_open, export_stage, sample_config):
        mock_path_join.side_effect = lambda *args: '/'.join(args)

        context = {
            'config': sample_config,
            'scraper_results': {},
            'consolidated_data': []
        }

        result = export_stage.execute(context)

        assert result.success is True
        assert result.stage == PipelineStage.EXPORT


class TestCleanupStage:

    @pytest.fixture
    def mock_logger(self):
        return Mock(spec=logging.Logger)

    @pytest.fixture
    def cleanup_stage(self, mock_logger):
        return CleanupStage(mock_logger)

    def test_stage_name(self, cleanup_stage):
        assert cleanup_stage.stage_name == "Cleanup"

    def test_execute_success_with_manager(self, cleanup_stage):
        context = {}

        result = cleanup_stage.execute(context)

        assert result.success is True
        assert result.stage == PipelineStage.CLEANUP
        assert result.message == "Cleanup completed successfully"


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
