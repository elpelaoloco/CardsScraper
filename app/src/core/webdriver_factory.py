from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional


class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(headless: bool = True, user_agent: Optional[str] = None,
                             window_size: str = "1280,720") -> webdriver.Chrome:
        options = Options()

        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=512")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")

        options.add_argument("--disable-features=site-per-process")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-remote-fonts")

        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--disable-infobars")

        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.geolocation': 2,
            'profile.managed_default_content_settings.media_stream': 2,
            'profile.default_content_settings.popups': 0,
        }
        options.add_experimental_option('prefs', prefs)

        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        else:
            options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        service = Service('/usr/bin/chromedriver')

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        return driver
