"""
Logging configuration with structured logging and log rotation.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "product_id"):
            log_data["product_id"] = record.product_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    enable_json: bool = False,
    enable_rotation: bool = True,
) -> None:
    """
    Configure application logging with rotation and structured output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files. If None, logs only to console
        enable_json: Use JSON formatter for structured logging
        enable_rotation: Enable log file rotation (daily rotation)
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if enable_json:
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (if log_dir is specified)
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        if enable_rotation:
            # Rotating file handler - daily rotation, keep 30 days
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=log_path / "pricewatch.log",
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
            )
        else:
            file_handler = logging.FileHandler(filename=log_path / "pricewatch.log", encoding="utf-8")

        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file

        if enable_json:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Error file handler - only errors and critical
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_path / "pricewatch_errors.log",
            when="midnight",
            interval=1,
            backupCount=90,  # Keep errors for 90 days
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Context managers for adding extra context to logs
class LogContext:
    """Context manager for adding extra fields to log records."""

    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger
        self.extra = kwargs
        self.old_factory = None

    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.extra.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)
