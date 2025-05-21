import os
import json
from src.core.scraper_manager import ScraperManager
from src.core.logger_factory import LoggerFactory
def create_example_config() -> None:
    config = {
        'scrapers': {
            'guild_dreams': {
                'type': 'guild_dreams',
                'headless': True,
                'page_load_delay': 3,
                'batch_size': 10,
                'categories': {
                    'magic': {
                        'url': 'https://www.guildreams.com/collection/magic-the-gathering?order=id&way=DESC&limit=106&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
                        }
                    },
                    "yugioh":{
                        'url': 'https://www.guildreams.com/collection/yu-gi-oh?order=id&way=DESC&limit=130&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
                        }
                    },
                    "pokemon":{
                        'url': 'https://www.guildreams.com/collection/pokemon?order=id&way=DESC&limit=167&page=1',
                        'selectors': {
                            'product_selector': '//div[@class="row"]//div[@class="bs-product"]',
                            'urls_selector': '//div[@class="row"]//div[@class="bs-product"]//div[@class="bs-product-info"]//a',
                            'price_selector': '//div[@data-bs="product.completePrice"]//div[@class="h5"] | //div[@data-bs="product.completePrice"]//span[@data-bs="product.finalPrice"] | //div[contains(., "Ahora")]/span[@class="h2"]',
                            'stock_selector': '//div[@data-bs="product.stock"]',
                            'description_selector': '//section[@id="bs-product-description"]',
                            'title_selector': '//article/h2',
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
        logger.info(f"Scraping completed. Results: {results.keys()}")
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)


if __name__ == "__main__":
    main()