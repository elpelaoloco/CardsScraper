from typing import Dict
class Category:
    
    def __init__(self, name: str, url: str, selectors: Dict[str, str]):

        self.name = name
        self.url = url
        self.selectors = selectors