import logging
from datetime import datetime


class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"


def setup_logger():
    # Logging configuration
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Custom UTC formatter
    formatter = UTCFormatter("%(asctime)s - %(levelname)s - %(message)s")

    # Terminal output
    th = logging.StreamHandler()
    th.setLevel(logging.INFO)
    th.setFormatter(formatter)
    logger.addHandler(th)

    # File output
    fh = logging.FileHandler(f"logs/logs{datetime.now().strftime('%Y_%m_%d__%H_%M')}.log")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # logger.info("=== LOGGING STARTED ===")

    return logger


logger = setup_logger()
