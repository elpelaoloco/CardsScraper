import logging
from src.core.scraper_manager import ScraperManager
import pandas as pd
from src.utils.save_results import save_dict_as_json
import os

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def consolidate_results(results: dict, output_path="data/consolidated_results.xlsx"):
    all_rows = []

    for scraper_name, categories_dict in results.items():
        if not categories_dict:
            continue
        for category_name, products in categories_dict.items():
            if not products:
                continue
            for item in products:
                item['store'] = scraper_name
                item['category'] = category_name
                all_rows.append(item)

    os.makedirs("data", exist_ok=True)
    if not all_rows:
        logger.warning("No data found to export. Creating empty Excel file.")
        empty_df = pd.DataFrame(
            columns=["name", "price", "url", "store", "category", "timestamp"])
        empty_df.to_excel(output_path, index=False)
    else:
        df = pd.DataFrame(all_rows)
        df.to_excel(output_path, index=False)
        logger.info(f"Excel consolidado guardado en {output_path}")


def main():
    config_path = "configs/scrapers_config.json"
    manager = ScraperManager(config_path)

    try:
        results = manager.run_all()
        json_file = "data/prod_result.json"
        os.makedirs("data", exist_ok=True)
        save_dict_as_json(results, "data/prod_result_2.json")
        manager.make_report()
    except Exception as e:
        logger.error(f"Fatal error during scraping execution: {e}", exc_info=True)

    logger.info("Scraping completed. Results: %s", results.keys())


if __name__ == "__main__":
    main()
