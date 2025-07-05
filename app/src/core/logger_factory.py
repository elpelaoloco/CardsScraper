import os
import logging
import datetime


class LoggerFactory:
    @staticmethod
    def create_logger(name: str, log_dir: str = 'logs') -> logging.Logger:

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = f"{log_dir}/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(logging.INFO)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
