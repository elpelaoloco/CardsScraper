import time
import random
from bs4 import BeautifulSoup
import os
import logging
from playwright.sync_api import sync_playwright
from src.utils.save_soup import save_soup_to_file


class RequestsHTMLSession:
    def __init__(self, debug=False):
        self._setup_encoding()
        self._setup_logging(debug)
        self.playwright = None
        self.browser = None
        self.context = None
        self.last_request_time = 0
        self._page_count = 0
        self._max_pages_per_browser = 10

    def _setup_encoding(self):
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'

    def _setup_logging(self, debug):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None

    def _log(self, message):
        if self.logger:
            self.logger.info(message)
        elif self.debug:
            print(message)

    def _init_playwright(self):
        if self.playwright is None or self._page_count >= self._max_pages_per_browser:
            if self.playwright is not None:
                self._cleanup_playwright()
                self._log("Reiniciando browser por límite de páginas")
            
            self._log("Inicializando Playwright...")
            self.playwright = sync_playwright().start()

            browser_args = [
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
                '--disable-dev-tools',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--disable-default-apps',
                '--disable-sync',
                '--no-first-run',
                '--disable-background-networking'
            ]

            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=browser_args
            )

            self.context = self.browser.new_context(
                viewport={'width': 1024, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='es-CL',
                timezone_id='America/Santiago',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )

            self._setup_resource_blocking()
            self._inject_stealth_scripts()
            
            self._page_count = 0
            self._log("Playwright inicializado")

    def _setup_resource_blocking(self):
        self.context.route("**/*.{png,jpg,jpeg,gif,svg,webp,ico,bmp,tiff}", 
                          lambda route: route.abort())
        
        blocking_domains = [
            "**/google-analytics.com/**",
            "**/googletagmanager.com/**",
            "**/facebook.com/**",
            "**/instagram.com/**",
            "**/tiktok.com/**",
            "**/twitter.com/**",
            "**/doubleclick.net/**",
            "**/adsystem.amazon.com/**",
            "**/amazon-adsystem.com/**",
            "**/googlesyndication.com/**",
            "**/hotjar.com/**",
            "**/zendesk.com/**",
            "**/intercom.io/**"
        ]
        
        for domain in blocking_domains:
            self.context.route(domain, lambda route: route.abort())

    def _inject_stealth_scripts(self):
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['es-ES', 'es', 'en'],
        });
        
        window.chrome = {
            runtime: {},
        };
        
        delete navigator.__proto__.webdriver;
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }
            ]
        });
        """
        
        self.context.add_init_script(stealth_script)

    def get(self, url, wait_for=None, render_js=True, wait_time=2):
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                self._apply_rate_limit()

                if attempt > 0:
                    delay = 2 * (2 ** attempt) + random.uniform(0.5, 1.5)
                    self._log(f"Reintento {attempt + 1}, esperando {delay:.1f}s...")
                    time.sleep(delay)

                if render_js:
                    return self._get_with_playwright(url, wait_for, wait_time)
                else:
                    return self._get_with_requests(url)

            except Exception as e:
                self._log(f"Intento {attempt + 1} falló: {e}")

                if "browser" in str(e).lower() or "context" in str(e).lower():
                    self._cleanup_playwright()

                if attempt == max_attempts - 1:
                    raise
                continue

        raise Exception(f"Failed to load page after {max_attempts} attempts")

    def _get_with_requests(self, url):
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')

    def _get_with_playwright(self, url, wait_for=None, wait_time=2):
        self._init_playwright()

        page = None
        try:
            page = self.context.new_page()
            self._page_count += 1

            page.set_default_timeout(20000)
            page.set_default_navigation_timeout(30000)

            self._log(f"Navegando a: {url}")
            
            try:
                response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                if response and response.status >= 400:
                    raise Exception(f"HTTP {response.status}")
                    
            except Exception as e:
                if "timeout" in str(e).lower():
                    self._log("Timeout en navegación, intentando con networkidle...")
                    page.goto(url, wait_until='networkidle', timeout=45000)
                else:
                    raise

            page.wait_for_timeout(wait_time * 1000)

            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=10000)
                    self._log(f"Selector encontrado: {wait_for}")
                except Exception:
                    self._log(f"Selector {wait_for} no encontrado, continuando...")

            try:
                page.evaluate("window.scrollTo(0, 300)")
                page.wait_for_timeout(1000)
            except:
                pass

            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')

            if self._is_complete_page(soup):
                self._log(f"Página cargada exitosamente ({len(content)} caracteres)")
                return soup
            else:
                raise Exception("Página incompleta detectada")

        finally:
            if page:
                try:
                    page.close()
                except:
                    pass

    def _apply_rate_limit(self):
        min_delay = 2.0
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _is_complete_page(self, soup):
        save_soup_to_file(soup, 'debug_page.html', prettify=True, debug=self.debug)
        if not soup.find('body') or not soup.find('head'):
            return False

        if len(str(soup)) < 500:
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
            self._page_count = 0
            self._log("Recursos de Playwright limpiados")
        except Exception as e:
            self._log(f"Error en limpieza: {e}")

    def close(self):
        self._cleanup_playwright()


class LightweightPlaywrightSession(RequestsHTMLSession):
    def __init__(self, debug=False):
        super().__init__(debug)

    def get_light(self, url, render_js=False):
        try:
            if not render_js:
                self._log("Intentando con requests simple...")
                soup = self._get_with_requests(url)

                if (len(soup.get_text()) > 1000 and 
                    soup.find_all(['div', 'article', 'section', 'main'])):
                    self._log("Contenido obtenido exitosamente con requests")
                    return soup
                else:
                    self._log("Contenido insuficiente con requests, fallback a Playwright")

            return self.get(url, render_js=True, wait_time=1)

        except Exception as e:
            self._log(f"Error en get_light: {e}")
            raise

    def scrape_safe(self, url, max_retries=2):
        strategies = [
            {'render_js': False, 'description': 'requests simple'},
            {'render_js': True, 'wait_time': 1, 'description': 'playwright rápido'},
            {'render_js': True, 'wait_time': 3, 'description': 'playwright lento'},
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                self._log(f"Estrategia {i+1}: {strategy['description']}")
                
                if strategy['render_js']:
                    return self.get(url, **{k: v for k, v in strategy.items() if k != 'description'})
                else:
                    return self._get_with_requests(url)
                    
            except Exception as e:
                self._log(f"Estrategia {i+1} falló: {e}")
                if i < len(strategies) - 1:
                    time.sleep(2)
                    continue
                else:
                    raise


def create_lightweight_session(debug=False):
    return LightweightPlaywrightSession(debug=debug)


def quick_scrape(url, render_js=False, debug=False):
    session = create_lightweight_session(debug=debug)
    try:
        return session.get_light(url, render_js=render_js)
    finally:
        session.close()
