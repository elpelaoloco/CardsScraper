import pytest
import os
import locale
from unittest.mock import patch, Mock

from src.utils.encoding import EncodingUtil


class TestEncodingUtil:
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('locale.setlocale')
    def test_setup_environment_success(self, mock_setlocale):
        EncodingUtil.setup_environment()
        
        assert os.environ['PYTHONIOENCODING'] == 'utf-8'
        assert os.environ['LANG'] == 'en_US.UTF-8'
        assert os.environ['LC_ALL'] == 'en_US.UTF-8'
        mock_setlocale.assert_called_with(locale.LC_ALL, 'en_US.UTF-8')
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('locale.setlocale')
    def test_setup_environment_fallback_locale(self, mock_setlocale):
        mock_setlocale.side_effect = [Exception("First locale failed"), None]
        
        EncodingUtil.setup_environment()
        
        assert os.environ['PYTHONIOENCODING'] == 'utf-8'
        assert mock_setlocale.call_count == 2
        mock_setlocale.assert_any_call(locale.LC_ALL, 'en_US.UTF-8')
        mock_setlocale.assert_any_call(locale.LC_ALL, 'C.UTF-8')
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('locale.setlocale')
    def test_setup_environment_all_locales_fail(self, mock_setlocale):
        mock_setlocale.side_effect = Exception("All locales failed")
        
        EncodingUtil.setup_environment()
        
        assert os.environ['PYTHONIOENCODING'] == 'utf-8'
        assert mock_setlocale.call_count == 2
    
    @patch('chardet.detect')
    def test_detect_encoding_success(self, mock_detect):
        mock_detect.return_value = {'encoding': 'iso-8859-1', 'confidence': 0.95}
        
        result = EncodingUtil.detect_encoding(b'test content')
        
        assert result == 'iso-8859-1'
        mock_detect.assert_called_once_with(b'test content')
    
    @patch('chardet.detect')
    def test_detect_encoding_no_encoding(self, mock_detect):
        mock_detect.return_value = {'confidence': 0.95}
        
        result = EncodingUtil.detect_encoding(b'test content')
        
        assert result == 'utf-8'
    
    @patch('chardet.detect')
    def test_detect_encoding_low_confidence(self, mock_detect):
        mock_detect.return_value = {'encoding': 'ascii', 'confidence': 0.3}
        
        result = EncodingUtil.detect_encoding(b'test content')
        
        assert result == 'utf-8'
    
    @patch('chardet.detect')
    def test_detect_encoding_exception(self, mock_detect):
        mock_detect.side_effect = Exception("Detection failed")
        
        result = EncodingUtil.detect_encoding(b'test content')
        
        assert result == 'utf-8'
    
    def test_safe_decode_with_utf8(self):
        content = "Hello World".encode('utf-8')
        result = EncodingUtil.safe_decode(content)
        assert result == "Hello World"
    
    def test_safe_decode_with_latin1(self):
        content = "Café".encode('latin-1')
        result = EncodingUtil.safe_decode(content, 'latin-1')
        assert "Café" in result or "Caf" in result
    
    def test_safe_decode_with_fallback(self):
        content = b'\xff\xfe'  # Invalid UTF-8
        result = EncodingUtil.safe_decode(content)
        assert isinstance(result, str)
    
    def test_clean_text_basic(self):
        text = "  Hello World  "
        result = EncodingUtil.clean_text(text)
        assert result == "Hello World"
    
    def test_clean_text_empty(self):
        result = EncodingUtil.clean_text("")
        assert result == ""
    
    def test_clean_text_none(self):
        result = EncodingUtil.clean_text(None)
        assert result == ""
    
    def test_validate_text_valid(self):
        result = EncodingUtil.validate_text("This is a valid text with enough characters")
        assert result is True
    
    def test_validate_text_too_short(self):
        result = EncodingUtil.validate_text("short")
        assert result is False
    
    def test_validate_text_with_invalid_chars(self):
        result = EncodingUtil.validate_text("This text has � invalid character")
        assert result is False
    
    def test_validate_text_with_null(self):
        result = EncodingUtil.validate_text("This text contains null value")
        assert result is False