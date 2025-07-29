import logging
import sys


def setup_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("loud_noise_detector")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
