import logging

from src.utils.logger import setup_logger


class TestLogger:
    def test_setup_logger_default(self) -> None:
        logger = setup_logger()

        assert logger.name == "loud_noise_detector"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].level == logging.INFO

    def test_setup_logger_verbose(self) -> None:
        logger = setup_logger(verbose=True)

        assert logger.name == "loud_noise_detector"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].level == logging.DEBUG
