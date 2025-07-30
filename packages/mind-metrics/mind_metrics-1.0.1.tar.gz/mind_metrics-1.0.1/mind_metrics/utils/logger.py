"""Logging configuration utilities."""

import logging
import warnings
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(verbose_level: int = 0) -> str:
    """Set up logging configuration based on verbosity level.

    Args:
        verbose_level: Verbosity level (0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG)

    Returns:
        The configured log level name
    """
    # Configure warnings based on verbosity
    if verbose_level >= 2:  # -vv or -vvv: show warnings
        warnings.resetwarnings()
    else:  # default, -v: hide warnings
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
    # Map verbosity levels to logging levels
    level_map = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }

    # Get the appropriate logging level
    log_level = level_map.get(verbose_level, logging.INFO)
    level_name = logging.getLevelName(log_level)

    # Configure rich handler for beautiful console output
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=verbose_level >= 3,  # Show path only for debug level
        rich_tracebacks=True,
        tracebacks_show_locals=verbose_level >= 3,
    )

    # Set up logging format
    if verbose_level >= 3:
        log_format = "%(name)s: %(message)s"
    else:
        log_format = "%(message)s"

    rich_handler.setFormatter(logging.Formatter(log_format))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add rich handler
    root_logger.addHandler(rich_handler)

    # Configure specific loggers to reduce noise
    if verbose_level < 3:
        # Quiet down some noisy third-party loggers
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

    return level_name


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name. If None, uses the calling module's name.

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(func):
    """Decorator to log function calls at debug level."""

    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise

    return wrapper
