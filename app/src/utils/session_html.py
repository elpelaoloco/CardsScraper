from requests_html import HTMLSession
import time
import random
from bs4 import BeautifulSoup
import os
import pyppeteer

class RequestsHTMLSession:
    def __init__(self):
        self._setup_encoding()
        self._patch_pyppeteer()
        self.session = HTMLSession()
        self._setup_session()
        self.last_request_time = 0
    
    def _setup_encoding(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    def _patch_pyppeteer(self):
        """Parche para pyppeteer con argumentos seguros para servidores"""
        original_launch = pyppeteer.launch

        async def safe_launch(**kwargs):
            safe_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--window-size=1920,1080',
                '--single-process',
                '--no-zygote',
                '--disable-dev-tools',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--memory-pressure-off',
                '--max_old_space_size=4096',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ]
            
            existing_args = kwargs.get('args', [])
            kwargs['args'] = safe_args + existing_args
            
            kwargs['headless'] = True
            kwargs['handleSIGINT'] = False
            kwargs['handleSIGTERM'] = False
            kwargs['handleSIGHUP'] = False
            
            return await original_launch(**kwargs)

        pyppeteer.launch = safe_launch
    
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
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
    
    def get(self, url, wait_for=None, render_js=True, wait_time=2):
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                self._apply_rate_limit()
                
                if attempt > 0:
                    delay = 2 * (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                
                r = self.session.get(url, timeout=30)
                r.raise_for_status()
                
                if render_js:
                    render_params = {
                        'timeout': 20,
                        'wait': wait_time,
                        'sleep': 1,
                        'keep_page': True,
                        'reload': False
                    }
                    
                    try:
                        r.html.render(**render_params)
                    except Exception as e:
                        print(f"Error rendering page: {e}")
                        os.system("pkill -f chrome 2>/dev/null || true")
                        if attempt == max_attempts - 1:
                            raise
                        continue
                    
                    if wait_for:
                        if not self._wait_for_selector(r.html, wait_for):
                            continue
                
                soup = BeautifulSoup(r.html.html, 'html.parser')
                
                if self._is_complete_page(soup):
                    return soup
                else:
                    continue
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                os.system("pkill -f chrome 2>/dev/null || true")
                
                if attempt == max_attempts - 1:
                    raise
                continue
        
        raise Exception(f"Failed to load page after {max_attempts} attempts")
    
    def _wait_for_selector(self, html_obj, selector, max_wait=10):
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                elements = html_obj.find(selector)
                if elements:
                    return True
            except:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def _apply_rate_limit(self):
        min_delay = 2.0
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _is_complete_page(self, soup):
        if not soup.find('body') or not soup.find('head'):
            return False
        
        if len(str(soup)) < 3000:
            return False
        
        page_text = soup.get_text().lower()
        
        error_indicators = [
            'cloudflare', 'access denied', 'blocked', 'captcha',
            '404', '500', 'error', 'not found'
        ]
        
        for indicator in error_indicators:
            if indicator in page_text[:2000]:
                return False
        
        loading_indicators = [
            'loading', 'cargando', 'please wait',
            'javascript required', 'enable javascript'
        ]
        
        for indicator in loading_indicators:
            if indicator in page_text[:1000]:
                return False
        
        return True
    
    def close(self):
        if self.session:
            try:
                self.session.close()
            except:
                pass
            
        os.system("pkill -f chrome 2>/dev/null || true")