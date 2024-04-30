import logging
from datetime import datetime


class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"


def setup_logger(logger_name=None, logger_file_name=None):
    # Logging configuration
    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(logging.INFO)

    # Custom UTC formatter
    formatter = UTCFormatter("%(asctime)s - %(levelname)s - %(message)s")

    # Terminal output
    th = logging.StreamHandler()
    th.setLevel(logging.INFO)
    th.setFormatter(formatter)
    logger.addHandler(th)

    # File output
    file_name = logger_file_name or f"logs/logs{datetime.now().strftime('%Y_%m_%d__%H_%M')}.log"
    fh = logging.FileHandler(file_name)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # logger.info("=== LOGGING STARTED ===")

    return logger
