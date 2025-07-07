import time
import random
from bs4 import BeautifulSoup
import os
from playwright.sync_api import sync_playwright

class RequestsHTMLSession:
    def __init__(self):
        self._setup_encoding()
        self.playwright = None
        self.browser = None
        self.context = None
        self.last_request_time = 0
        
    def _setup_encoding(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    def _init_playwright(self):
        if self.playwright is None:
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--memory-pressure-off',
                    '--max_old_space_size=512',
                    '--single-process',
                    '--no-zygote',
                    '--window-size=1024,768',
                    '--disable-web-security',
                    '--disable-dev-tools'
                ]
            )
            
            self.context = self.browser.new_context(
                viewport={'width': 1024, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            self.context.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,ico}", 
                             lambda route: route.abort())
            
            self.context.route("**/google-analytics.com/**", lambda route: route.abort())
            self.context.route("**/googletagmanager.com/**", lambda route: route.abort())
            self.context.route("**/facebook.com/**", lambda route: route.abort())
            
    def get(self, url, wait_for=None, render_js=True, wait_time=2):
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                self._apply_rate_limit()
                
                if attempt > 0:
                    delay = 2 * (2 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                
                if render_js:
                    return self._get_with_playwright(url, wait_for, wait_time)
                else:
                    import requests
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    return BeautifulSoup(response.content, 'html.parser')
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
                self._cleanup_playwright()
                
                if attempt == max_attempts - 1:
                    raise
                continue
        
        raise Exception(f"Failed to load page after {max_attempts} attempts")
    
    def _get_with_playwright(self, url, wait_for=None, wait_time=2):
        self._init_playwright()
        
        page = None
        try:
            page = self.context.new_page()
            
            page.set_default_timeout(15000)
            page.set_default_navigation_timeout(20000)
            
            page.goto(url, wait_until='domcontentloaded')
            
            page.wait_for_timeout(wait_time * 1000)
            
            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=10000)
                except:
                    print(f"Selector {wait_for} no encontrado, continuando...")
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            if self._is_complete_page(soup):
                return soup
            else:
                raise Exception("Página incompleta")
                
        finally:
            if page:
                page.close()
    
    def _wait_for_selector(self, page, selector, max_wait=10):
        try:
            page.wait_for_selector(selector, timeout=max_wait * 1000)
            return True
        except:
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
        
        if len(str(soup)) < 1000:
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
    
    def _cleanup_playwright(self):
        try:
            if self.context:
                self.context.close()
                self.context = None
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except:
            pass
    
    def close(self):
        self._cleanup_playwright()

class LightweightPlaywrightSession(RequestsHTMLSession):
    def __init__(self):
        super().__init__()
    
    def get_light(self, url, render_js=False):
        try:
            if not render_js:
                import requests
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if len(soup.get_text()) > 1000 and soup.find_all(['div', 'article', 'section']):
                    return soup
            
            return self.get(url, render_js=True, wait_time=1)
            
        except Exception as e:
            print(f"Error en get_light: {e}")
            raise

def create_lightweight_session():
    return LightweightPlaywrightSession()
