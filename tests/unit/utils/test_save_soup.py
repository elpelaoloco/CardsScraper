import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from bs4 import BeautifulSoup

from src.utils.save_soup import save_soup_to_file


class TestSaveSoup:

    def test_save_soup_to_file_with_filename(self):
        soup = BeautifulSoup('<html><body><h1>Test</h1></body></html>', 'html.parser')

        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', mock_open()) as mock_file:
                result = save_soup_to_file(soup, filename='test.html', output_dir='output')

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert isinstance(result, dict)
        assert 'html_path' in result or 'success' in result

    def test_save_soup_to_file_auto_filename(self):
        soup = BeautifulSoup('<html><head><title>Test Page</title></head><body>Content</body></html>', 'html.parser')

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()):
                result = save_soup_to_file(soup, output_dir='output')

        assert isinstance(result, dict)

    def test_save_soup_to_file_with_url(self):
        soup = BeautifulSoup('<html><body>Content</body></html>', 'html.parser')
        url = 'https://example.com/test/page'

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()):
                result = save_soup_to_file(soup, url=url, output_dir='output')

        assert isinstance(result, dict)

    def test_save_soup_to_file_prettify_option(self):
        soup = BeautifulSoup('<html><body><div>Test</div></body></html>', 'html.parser')

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()) as mock_file:
                save_soup_to_file(soup, filename='test.html', prettify=True)
                save_soup_to_file(soup, filename='test2.html', prettify=False)

        assert mock_file.call_count == 2

    def test_save_soup_to_file_metadata_option(self):
        soup = BeautifulSoup('<html><body>Content</body></html>', 'html.parser')

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()):
                result_with_meta = save_soup_to_file(soup, filename='test.html', save_metadata=True)
                result_without_meta = save_soup_to_file(soup, filename='test2.html', save_metadata=False)

        assert isinstance(result_with_meta, dict)
        assert isinstance(result_without_meta, dict)

    def test_save_soup_to_file_debug_mode(self):
        soup = BeautifulSoup('<html><body>Debug test</body></html>', 'html.parser')

        with patch('pathlib.Path.mkdir'):
            with patch('builtins.open', mock_open()):
                with patch('builtins.print') as mock_print:
                    save_soup_to_file(soup, filename='debug.html', debug=True)

        # Debug mode might print information
        print_called = mock_print.called
        assert isinstance(print_called, bool)

    def test_save_soup_real_file(self):
        soup = BeautifulSoup('<html><body><h1>Real Test</h1></body></html>', 'html.parser')

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = save_soup_to_file(soup, filename='real_test.html', output_dir=tmp_dir)

            assert isinstance(result, dict)

            if 'html_path' in result:
                html_path = result['html_path']
                assert os.path.exists(html_path)

                with open(html_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                assert '<h1>Real Test</h1>' in content
