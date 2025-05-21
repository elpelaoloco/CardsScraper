import os
import json
from src.core.scraper_manager import ScraperManager
from src.core.logger_factory import LoggerFactory
def create_example_config() -> None:
    config = {
        'scrapers': {
         'thirdimpact': {
            'type': 'thirdimpact',
            'headless': True,
            'page_load_delay': 2,
            'categories': {
                'pokemon': {
                    'url': 'https://www.thirdimpact.cl/collection/pokemon',
                    'selectors': {
                        'product_selector':  "//section[contains(@class, 'grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'bs-product__final-price')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//section[@class='bs-product-description']",
                        'title_selector': "",
                        'language_selector': "//div[@id='bs-product-form' and contains(@class, 'form')]//input"
                    
                    }
                },
                'yugioh': {
                    'url': 'https://www.thirdimpact.cl/collection/yu-gi-oh',
                    'selectors': {
                        'product_selector': "//section[contains(@class, 'grid-item')]",
                        'urls_selector': ".//a[@class='bs-collection__product-info']",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"

                    }
                },
                'magic': {
                    'url': 'https://www.thirdimpact.cl/collection/magic-the-gathering',
                    'selectors': {
                        'product_selector': "//div[contains(@class, 'product-grid-item')]",
                        'urls_selector': ".//a[contains(@class, 'product-grid-item__title')]",
                        'price_selector': ".//div[contains(@class, 'price')]//span[contains(@class, 'money')]",
                        'stock_selector': ".//p[contains(text(), 'Agotado')]",
                        'description_selector': "//div[contains(@class, 'product-single__description')]",
                        'title_selector': "//h1[contains(@class, 'product-single__title')]"
                    }
                }
            }
        }
        }
    }
    

    if not os.path.exists('configs'):
        os.makedirs('configs')
    
    with open('configs/scrapers_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("Example configuration files created in 'configs' directory.")



def main() -> None:

    if not os.path.exists('configs/scrapers_config.json'):
        create_example_config()
    
    logger = LoggerFactory.create_logger("main")
    
    try:
        manager = ScraperManager('configs/scrapers_config.json')
        results = manager.run_all()
        manager.make_report()
        logger.info(f"Scraping completed. Results: {results.keys()}")
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)


if __name__ == "__main__":
    main()