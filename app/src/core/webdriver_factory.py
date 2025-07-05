from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional

class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(headless: bool = True, user_agent: Optional[str] = None,
                           window_size: str = "1920,1080") -> webdriver.Chrome:
        options = Options()
        prefs = {
            'profile.managed_default_content_settings.images': 2,  # 2 = block images
            'profile.default_content_setting_values.notifications': 2,  # 2 = block notifications
            # 'profile.managed_default_content_settings.stylesheets': 2,  # Opcional: deshabilitar CSS
            # 'profile.managed_default_content_settings.cookies': 2,  # Opcional: bloquear cookies
            'profile.managed_default_content_settings.geolocation': 2,  # Bloquear solicitudes de geolocalización
            'profile.managed_default_content_settings.media_stream': 2,  # Bloquear cámara/micrófono
        }
        options.add_experimental_option('prefs', prefs)
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--disable-infobars")
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-features=site-per-process')
        options.add_argument('--disable-remote-fonts')
        
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        else:
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        service = Service('/usr/bin/chromedriver')
        
        return webdriver.Chrome(service=service, options=options)