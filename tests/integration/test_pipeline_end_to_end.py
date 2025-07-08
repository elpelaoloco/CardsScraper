import pytest
import tempfile
import os
import json
from unittest.mock import patch, Mock, MagicMock
from bs4 import BeautifulSoup

from src.pipeline.pipeline import ScraperPipeline
from src.pipeline.models import PipelineConfig


class TestPipelineEndToEnd:

    @pytest.fixture
    def minimal_config(self):
        return PipelineConfig(
            config_path="configs/test_config.json",
            api_endpoint=None,
            output_dir="test_output"
        )

    @pytest.fixture
    def mock_scraper_results(self):
        return {
            'test_store': {
                'pokemon': [
                    {
                        'name': 'Pikachu Card',
                        'price': '$10.00',
                        'url': 'https://test.com/pikachu',
                        'img_url': 'https://test.com/pikachu.jpg',
                        'stock': 'in_stock',
                        'type': 'singles',
                        'store': 'test_store',
                        'game': 'pokemon'
                    },
                    {
                        'name': 'Charizard Card',
                        'price': '$50.00',
                        'url': 'https://test.com/charizard',
                        'img_url': 'https://test.com/charizard.jpg',
                        'stock': 'in_stock',
                        'type': 'singles',
                        'store': 'test_store',
                        'game': 'pokemon'
                    }
                ]
            }
        }

    @pytest.fixture
    def mock_scraper_report(self):
        return {
            'test_store': {
                'pokemon': {
                    'total_products': 2,
                    'processed_products': 2,
                    'success_rate': 100.0,
                    'categories_processed': 1,
                    'execution_time': 5.2
                }
            }
        }

    @patch('src.pipeline.stages.post_request.requests.post')
    @patch('src.pipeline.stages.export.pd.DataFrame.to_excel')
    @patch('builtins.open')
    @patch('os.makedirs')
    @patch('src.pipeline.stages.scraping.ScraperManager')
    def test_full_pipeline_execution_success(self, mock_scraper_manager_class, mock_makedirs,
                                             mock_open, mock_to_excel, mock_post,
                                             minimal_config, mock_scraper_results, mock_scraper_report):

        mock_manager = Mock()
        mock_manager.run_all.return_value = mock_scraper_results
        mock_manager.get_report.return_value = mock_scraper_report
        mock_scraper_manager_class.return_value = mock_manager

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response

        pipeline = ScraperPipeline(minimal_config)
        summary = pipeline.run()

        assert summary['total_stages'] == 6
        assert summary['successful_stages'] >= 5
        assert summary['total_items_processed'] == 2
        assert summary['scrapers_executed'] == 1

        stage_names = [stage['stage'] for stage in summary['stages_detail']]
        expected_stages = ['initialization', 'scraping', 'consolidation', 'export', 'post_request', 'cleanup']

        for expected_stage in expected_stages:
            assert expected_stage in stage_names

        mock_scraper_manager_class.assert_called_once()
        mock_manager.run_all.assert_called_once()
        mock_manager.get_report.assert_called_once()

        mock_makedirs.assert_called()
        mock_to_excel.assert_called()

    @patch('src.pipeline.stages.scraping.ScraperManager')
    def test_pipeline_failure_recovery(self, mock_scraper_manager_class, minimal_config):

        mock_manager = Mock()
        mock_manager.run_all.side_effect = Exception("Scraping failed")
        mock_scraper_manager_class.return_value = mock_manager

        pipeline = ScraperPipeline(minimal_config)
        summary = pipeline.run()

        assert summary['total_stages'] >= 1
        assert summary['failed_stages'] >= 1

        failed_stages = [stage for stage in summary['stages_detail'] if not stage['success']]
        assert len(failed_stages) >= 1

        scraping_stage = next((stage for stage in summary['stages_detail']
                              if stage['stage'] == 'scraping'), None)
        if scraping_stage:
            assert scraping_stage['success'] is False
            assert 'failed' in scraping_stage['error'].lower()

    @patch('src.pipeline.stages.export.pd.DataFrame.to_excel')
    @patch('builtins.open')
    @patch('os.makedirs')
    @patch('src.pipeline.stages.scraping.ScraperManager')
    def test_pipeline_data_flow(self, mock_scraper_manager_class, mock_makedirs,
                                mock_open, mock_to_excel,
                                minimal_config, mock_scraper_results, mock_scraper_report):

        mock_manager = Mock()
        mock_manager.run_all.return_value = mock_scraper_results
        mock_manager.get_report.return_value = mock_scraper_report
        mock_scraper_manager_class.return_value = mock_manager

        pipeline = ScraperPipeline(minimal_config)
        summary = pipeline.run()

        context = pipeline.context

        assert 'scraper_results' in context
        assert 'consolidated_data' in context
        assert 'report' in context
        assert 'scraping_time' in context

        assert context['scraper_results'] == mock_scraper_results
        assert len(context['consolidated_data']) == 2
        assert context['report'] == mock_scraper_report
        assert isinstance(context['scraping_time'], (int, float))

        consolidated_item = context['consolidated_data'][0]
        expected_fields = ['name', 'price', 'url', 'store', 'game']

        for field in expected_fields:
            assert field in consolidated_item

    @patch('src.pipeline.stages.scraping.ScraperManager')
    def test_pipeline_with_empty_results(self, mock_scraper_manager_class, minimal_config):

        mock_manager = Mock()
        mock_manager.run_all.return_value = {}
        mock_manager.get_report.return_value = {}
        mock_scraper_manager_class.return_value = mock_manager

        pipeline = ScraperPipeline(minimal_config)
        summary = pipeline.run()

        assert summary['total_items_processed'] == 0
        assert summary['scrapers_executed'] == 0
        assert summary['successful_stages'] >= 3

        context = pipeline.context
        assert context['scraper_results'] == {}
        assert context['consolidated_data'] == []

    def test_pipeline_config_validation(self):

        invalid_config = PipelineConfig(
            config_path="",
            output_dir=""
        )

        pipeline = ScraperPipeline(invalid_config)
        assert pipeline.config == invalid_config
        assert hasattr(pipeline, 'stages')
        assert len(pipeline.stages) == 6

    @patch('src.pipeline.stages.initialization.os.makedirs')
    def test_pipeline_initialization_stage(self, mock_makedirs, minimal_config):

        pipeline = ScraperPipeline(minimal_config)
        init_stage = pipeline.stages[0]

        result = init_stage.execute(pipeline.context)

        assert result.success is True
        assert result.stage.value == 'initialization'
        mock_makedirs.assert_called_once_with('test_output', exist_ok=True)
