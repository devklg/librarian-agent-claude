"""
Structured Logging Configuration for Librarian Agent
Uses structlog for structured, JSON-formatted logging
"""

import logging
import sys
from typing import Optional

# Try to import structlog, fall back to standard logging if not available
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' for production, 'console' for development)
    """

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    if STRUCTLOG_AVAILABLE:
        # Configure structlog processors
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]

        if log_format == "json":
            # JSON output for production
            processors = shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        else:
            # Console output for development
            processors = shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True),
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        A logger instance (structlog if available, otherwise standard logging)
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class LoggerAdapter:
    """
    Adapter that provides a consistent interface regardless of logging backend
    """

    def __init__(self, name: Optional[str] = None):
        self._logger = get_logger(name)
        self._structlog = STRUCTLOG_AVAILABLE

    def _log(self, level: str, message: str, **kwargs):
        """Internal log method that handles both backends"""
        if self._structlog:
            getattr(self._logger, level)(message, **kwargs)
        else:
            # Format kwargs for standard logging
            extra_info = " ".join(f"{k}={v}" for k, v in kwargs.items())
            full_message = f"{message} {extra_info}" if extra_info else message
            getattr(self._logger, level)(full_message)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log an exception with traceback"""
        if self._structlog:
            self._logger.exception(message, **kwargs)
        else:
            self._logger.exception(f"{message} {kwargs}")


# Initialize with defaults
configure_logging()
