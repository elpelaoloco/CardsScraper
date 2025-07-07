import re
from typing import List, Optional, Union
from bs4 import BeautifulSoup, Tag, NavigableString


class CSSContainsHandler:

    @staticmethod
    def select(soup: BeautifulSoup, selector: str) -> List[Tag]:
        if ':contains(' not in selector:
            return soup.select(selector)

        return CSSContainsHandler._handle_contains_selector(soup, selector)

    @staticmethod
    def select_one(soup: BeautifulSoup, selector: str) -> Optional[Tag]:
        elements = CSSContainsHandler.select(soup, selector)
        return elements[0] if elements else None

    @staticmethod
    def _handle_contains_selector(soup: BeautifulSoup, selector: str) -> List[Tag]:
        contains_pattern = r'([^:]+):contains\([\'"]([^\'"]+)[\'"]\)'
        match = re.search(contains_pattern, selector)

        if not match:
            return soup.select(selector.replace(':contains(', '').replace(')', ''))

        base_selector = match.group(1).strip()
        contains_text = match.group(2)

        if base_selector:
            candidates = soup.select(base_selector)
        else:
            candidates = soup.find_all()

        matching_elements = []
        for element in candidates:
            if CSSContainsHandler._element_contains_text(element, contains_text):
                matching_elements.append(element)

        return matching_elements

    @staticmethod
    def _element_contains_text(element: Tag, text: str, case_sensitive: bool = False) -> bool:
        if not isinstance(element, Tag):
            return False

        element_text = element.get_text()

        if case_sensitive:
            return text in element_text
        else:
            return text.lower() in element_text.lower()

    @staticmethod
    def find_by_text_content(soup: BeautifulSoup,
                             tag_name: str,
                             text: str,
                             exact_match: bool = False,
                             case_sensitive: bool = False) -> List[Tag]:
        if exact_match:
            if case_sensitive:
                return soup.find_all(tag_name, string=text)
            else:
                return soup.find_all(tag_name, string=re.compile(f'^{re.escape(text)}$', re.IGNORECASE))
        else:
            if case_sensitive:
                return soup.find_all(tag_name, string=re.compile(re.escape(text)))
            else:
                return soup.find_all(tag_name, string=re.compile(re.escape(text), re.IGNORECASE))


class StockChecker:

    STOCK_OUT_PATTERNS = [
        'agotado',
        'out of stock',
        'sin stock',
        'no disponible',
        'sold out',
        'no stock',
        'fuera de stock'
    ]

    @staticmethod
    def is_out_of_stock(soup: BeautifulSoup, selector: str = None) -> bool:
        if selector:
            if ':contains(' in selector:
                elements = CSSContainsHandler.select(soup, selector)
                return len(elements) > 0
            else:
                elements = soup.select(selector)
                for element in elements:
                    if StockChecker._check_element_for_stock_out(element):
                        return True
                return False

        return StockChecker._search_entire_page_for_stock_out(soup)

    @staticmethod
    def _check_element_for_stock_out(element: Tag) -> bool:
        if not isinstance(element, Tag):
            return False

        text = element.get_text().lower()

        for pattern in StockChecker.STOCK_OUT_PATTERNS:
            if pattern in text:
                return True

        return False

    @staticmethod
    def _search_entire_page_for_stock_out(soup: BeautifulSoup) -> bool:
        common_stock_selectors = [
            'p', 'span', 'div.stock', 'div.availability',
            '.out-of-stock', '.sold-out', '.no-stock'
        ]

        for selector in common_stock_selectors:
            elements = soup.select(selector)
            for element in elements:
                if StockChecker._check_element_for_stock_out(element):
                    return True

        return False


class EnhancedSelector:

    @staticmethod
    def select(soup: BeautifulSoup, selector: str) -> List[Tag]:
        if ',' in selector:
            all_elements = []
            for sub_selector in selector.split(','):
                sub_selector = sub_selector.strip()
                elements = EnhancedSelector._select_single(soup, sub_selector)
                all_elements.extend(elements)
            return all_elements

        return EnhancedSelector._select_single(soup, selector)

    @staticmethod
    def select_one(soup: BeautifulSoup, selector: str) -> Optional[Tag]:
        elements = EnhancedSelector.select(soup, selector)
        return elements[0] if elements else None

    @staticmethod
    def _select_single(soup: BeautifulSoup, selector: str) -> List[Tag]:
        if ':contains(' in selector:
            return CSSContainsHandler.select(soup, selector)

        if ':first-child' in selector:
            return EnhancedSelector._handle_first_child(soup, selector)

        return soup.select(selector)

    @staticmethod
    def _handle_first_child(soup: BeautifulSoup, selector: str) -> List[Tag]:
        base_selector = selector.replace(':first-child', '')
        elements = soup.select(base_selector)

        first_children = []
        for element in elements:
            parent = element.parent
            if parent:
                siblings = [child for child in parent.children if isinstance(child, Tag) and child.name == element.name]
                if siblings and siblings[0] == element:
                    first_children.append(element)

        return first_children


class ImprovedBaseScraper:

    def find_elements(self, soup: BeautifulSoup, selector: str) -> List[Tag]:
        try:
            return EnhancedSelector.select(soup, selector)
        except Exception as e:
            self.logger.warning(f"Error finding elements with selector {selector}: {e}")
            return []

    def find_element(self, soup: BeautifulSoup, selector: str) -> Optional[Tag]:
        elements = self.find_elements(soup, selector)
        return elements[0] if elements else None

    def check_stock(self, soup: BeautifulSoup, stock_selector: str = None) -> str:
        if StockChecker.is_out_of_stock(soup, stock_selector):
            return "out_of_stock"
        else:
            return "in_stock"

    def find_by_text(self, soup: BeautifulSoup, tag: str, text: str) -> List[Tag]:
        return CSSContainsHandler.find_by_text_content(soup, tag, text)


def select_with_contains(soup: BeautifulSoup, selector: str) -> List[Tag]:
    return CSSContainsHandler.select(soup, selector)


def select_one_with_contains(soup: BeautifulSoup, selector: str) -> Optional[Tag]:
    return CSSContainsHandler.select_one(soup, selector)


def check_if_out_of_stock(soup: BeautifulSoup, selector: str = None) -> bool:
    return StockChecker.is_out_of_stock(soup, selector)
