import os
import sys
import locale
import chardet
import re
from typing import Optional, Union


class EncodingUtil:
    @staticmethod
    def setup_environment():
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'

        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except Exception:
            try:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            except Exception :
                pass

    @staticmethod
    def detect_encoding(content: bytes) -> str:
        try:
            result = chardet.detect(content)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)

            if confidence < 0.6:
                encoding = 'utf-8'

            return encoding.lower() if encoding else 'utf-8'
        except Exception as e:
            return 'utf-8'

    @staticmethod
    def safe_decode(content: bytes, encoding: Optional[str] = None) -> str:
        if encoding is None:
            encoding = EncodingUtil.detect_encoding(content)

        encodings_to_try = [
            encoding,
            'utf-8',
            'latin-1',
            'iso-8859-1',
            'cp1252',
            'windows-1252',
            'ascii'
        ]

        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                decoded = content.decode(enc, errors='strict')
                if len(decoded.strip()) > 0:
                    return decoded
            except (UnicodeDecodeError, LookupError):
                continue

        return content.decode('utf-8', errors='replace')

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        replacements = {
            '\x00': '',
            '\ufeff': '',
            '\u200b': '',
            '\u200c': '',
            '\u200d': '',
            '\xa0': ' ',
            '\r\n': ' ',
            '\r': ' ',
            '\n': ' ',
            '\t': ' '
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def validate_text(text: str) -> bool:
        if not text or len(text.strip()) < 10:
            return False

        invalid_indicators = [
            '�',
            '\ufffd',
            'null',
            'undefined'
        ]

        for indicator in invalid_indicators:
            if indicator in text.lower():
                return False

        return True
