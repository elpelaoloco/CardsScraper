
import os
from dotenv import load_dotenv
from src.pipeline import ScraperPipeline, PipelineConfig
load_dotenv()


def main():
    base_url = os.getenv("API_URL", "https://te-odio-docker-back-git-main-teodiodockers-projects.vercel.app/")

    config = PipelineConfig(
        config_path=os.getenv("CONFIG_PATH", "configs/test_config.json"),
        api_endpoint=f"{base_url}scrapper/bulk",
        api_headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer your-token-here"
        },
        output_dir="data",
        json_filename="prod_result.json",
        excel_filename="consolidated_results.xlsx",
        request_timeout=30
    )

    pipeline = ScraperPipeline(config)
    summary = pipeline.run()

    print("\n" + "=" * 50)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 50)
    print(f"Total stages: {summary['total_stages']}")
    print(f"Successful: {summary['successful_stages']}")
    print(f"Failed: {summary['failed_stages']}")
    print(f"Items processed: {summary['total_items_processed']}")
    print(f"Scrapers executed: {summary['scrapers_executed']}")
    print(f"Scraping time: {summary.get('scraping_time', 'N/A'):.4f} seconds")
    for report in summary['detailed_reports']:
        print(f"Scraper: {report['scraper']}")
        print(f"{' '* 4} Game: {report['game']}")
        print(f"{' ' * 5} - Total Products: {report['report']['total_products']}  Processed Products:{report['report']['processed_products']}  Success Rate:{report['report']['success_rate']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
