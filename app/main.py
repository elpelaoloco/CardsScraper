
from src.pipeline import ScraperPipeline, PipelineConfig
import os


def main():
    """Main execution function"""
    # Configuration
    config = PipelineConfig(
        config_path="configs/test_config.json",
        api_endpoint=os.getenv("API_URL", "http://localhost:8000/scrapper/bulk"), 
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
    
    print("\n" + "="*50)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*50)
    print(f"Total stages: {summary['total_stages']}")
    print(f"Successful: {summary['successful_stages']}")
    print(f"Failed: {summary['failed_stages']}")
    print(f"Items processed: {summary['total_items_processed']}")
    print(f"Scrapers executed: {summary['scrapers_executed']}")
    print("="*50)


if __name__ == "__main__":
    main()