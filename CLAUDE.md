# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```
Main entry point that executes the scraping pipeline using configuration from `configs/test_config.json` by default.

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_card_universe.py

# Run tests with custom report (legacy approach)
python tests/run_all_tests.py
```

Test configuration is in `pytest.ini` with coverage reporting, verbose output, and test markers for unit/integration tests.

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# For test dependencies
pip install -r requirements-test.txt
```

## Architecture

### Core Components

**Pipeline Architecture**: The application uses a multi-stage pipeline pattern (`src/pipeline/`) with stages:
- InitializationStage: Loads configuration and initializes scrapers
- ScrapingStage: Executes all configured scrapers
- ConsolidationStage: Merges results from multiple scrapers
- ExportStage: Saves data to JSON and Excel formats
- PostRequestStage: Sends results to external API
- CleanupStage: Cleanup operations

**Scraper Management**: 
- `ScraperManager` (`src/core/scraper_manager.py`) orchestrates multiple scrapers
- `ScraperFactory` creates scraper instances based on configuration
- Each scraper inherits from `BaseScraper` and implements store-specific logic

**Configuration-Driven**: All scrapers are configured via JSON files in `configs/`:
- `scrapers_config.json`: Main scraper definitions with URLs and CSS selectors
- `test_config.json`/`prod_config.json`: Environment-specific configurations

### Scraper Structure

Each scraper in `src/scrapers/` handles a specific online store:
- `card_universe.py`, `thirdimpact.py`, `la_comarca.py`, etc.
- Supports multiple game categories (Pokemon, Magic, Yu-Gi-Oh)
- Uses Playwright for web automation
- Implements retry logic and error handling

### Data Flow

1. **Configuration Loading**: Pipeline loads JSON config specifying scrapers and their selectors
2. **Scraper Execution**: Each scraper visits configured URLs and extracts product data
3. **Data Consolidation**: Results are merged into a unified format
4. **Export**: Data is saved to JSON/Excel and optionally sent to external API
5. **Reporting**: Detailed execution reports are generated in `reports/`

### Key Patterns

- **Factory Pattern**: `ScraperFactory` creates scraper instances
- **Strategy Pattern**: Each scraper implements different extraction strategies
- **Pipeline Pattern**: Sequential stage execution with context passing
- **Configuration-based**: Scrapers behavior controlled via JSON config files

### Environment Variables

- `API_URL`: Base URL for external API (default: Vercel app)
- `CONFIG_PATH`: Path to config file (default: `configs/test_config.json`)

### Directory Structure

- `src/core/`: Core framework (managers, factories, base classes)
- `src/scrapers/`: Store-specific scraper implementations
- `src/pipeline/`: Pipeline stages and orchestration
- `configs/`: Configuration files with scraper definitions
- `tests/`: Unit and integration tests with pytest
- `logs/`: Execution logs per scraper and pipeline
- `reports/`: JSON reports with scraping statistics
- `data/`: Output data files (JSON/Excel)

## Code Style Preferences

**No Comments or Docstrings**: The codebase should be written without inline comments or docstrings. Code should be self-documenting through clear naming and structure. All documentation should be placed in README.md or other external documentation files rather than within the code itself.