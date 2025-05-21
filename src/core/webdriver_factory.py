from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional
class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(headless: bool = True, user_agent: Optional[str] = None, 
                             window_size: str = "1920,1080") -> webdriver.Chrome:

        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={window_size}")
        
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        else:
            # Default user agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        return webdriver.Chrome(options=options)

