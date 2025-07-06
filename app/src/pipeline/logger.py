"""
Logger configuration for the pipeline
"""
import logging


def setup_logger(name: str = "scraper_pipeline", level: int = logging.INFO) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger