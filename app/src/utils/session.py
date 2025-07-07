import requests
import time
import random
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.utils.encoding import EncodingUtil


class SimpleReliableSession:
    def __init__(self):
        EncodingUtil.setup_environment()
        self.session = requests.Session()
        self._setup_session()
        self.last_request_time = 0
    
    def _setup_session(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'utf-8, iso-8859-1;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
        self.session.verify = True
        
    def get(self, url: str) -> BeautifulSoup:
        max_attempts = 3
        base_delay = 2.0
        
        for attempt in range(max_attempts):
            try:
                self._apply_rate_limit()
                
                if attempt > 0:
                    delay = base_delay * (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                if self._is_valid_response(response):
                    soup = self._create_soup_safe(response)
                    
                    if self._is_complete_page(soup):
                        return soup
                    else:
                        print(f"Page seems incomplete (attempt {attempt + 1})")
                        continue
                
            except requests.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    raise
                continue
            except Exception as e:
                print(f"Encoding/parsing error (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    raise
                continue
        
        raise Exception(f"Failed to load complete page after {max_attempts} attempts")
    
    def _create_soup_safe(self, response: requests.Response) -> BeautifulSoup:
        try:
            detected_encoding = response.encoding or response.apparent_encoding
            content_text = EncodingUtil.safe_decode(response.content, detected_encoding)
            content_text = EncodingUtil.clean_text(content_text)
            
            soup = BeautifulSoup(content_text, 'html.parser')
            
            if len(soup.get_text().strip()) > 100:
                return soup
                
        except Exception:
            pass
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except Exception as e:
            raise Exception(f"All encoding methods failed: {e}")
    
    def _apply_rate_limit(self):
        min_delay = 1.5
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _is_valid_response(self, response: requests.Response) -> bool:
        if not (200 <= response.status_code < 300):
            return False
        
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            return False
        
        if len(response.content) < 1000:
            return False
        
        return True
    
    def _is_complete_page(self, soup: BeautifulSoup) -> bool:
        if not soup.find('body') or not soup.find('head'):
            return False
        
        if len(str(soup)) < 5000:
            return False
        
        page_text = soup.get_text().lower()
        error_indicators = [
            'cloudflare', 'access denied', 'blocked', 'captcha',
            'please enable javascript', 'javascript required',
            '404', '500', 'error', 'not found'
        ]
        
        for indicator in error_indicators:
            if indicator in page_text[:2000]:
                return False
        
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            if any(error in title_text for error in ['error', '404', '500']):
                return False
        
        return True
    
    def close(self):
        if self.session:
            self.session.close()