"""
Lightweight reusable logger factory.

All modules in this package call ``get_logger(__name__)`` so that log
output can be filtered or redirected at the application level without
touching library code.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured with a sensible default format.

    If a handler is already attached (e.g. the caller configured logging
    globally) this function is a no-op for the handler setup.

    Parameters
    ----------
    name:
        Typically ``__name__`` of the calling module.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    if logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)

    return logger
