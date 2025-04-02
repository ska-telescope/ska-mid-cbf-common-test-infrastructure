"""Log format for all test repositories."""

import logging

LOG_FORMAT = "[%(asctime)s|%(levelname)s|%(filename)s#%(lineno)s] %(message)s"

FORMAT_HANDLER = logging.StreamHandler()
FORMAT_HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))


def setup_logger(logger: logging.Logger):
    """
    Setup up given logger with format of LOG_FORMAT and INFO logging level.

    :returns: given logger
    """
    logger.addHandler(FORMAT_HANDLER)
    logger.setLevel(logging.INFO)
    return logger
