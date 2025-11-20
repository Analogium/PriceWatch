"""
Unit tests for logging configuration.
Tests JSON formatter, logging setup, and context managers.
"""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.core.logging_config import JSONFormatter, LogContext, get_logger, setup_logging


@pytest.mark.unit
class TestJSONFormatter:
    """Test suite for JSONFormatter class."""

    def test_json_formatter_basic_format(self):
        """Test basic JSON formatting of log records."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/app/test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42
        assert "timestamp" in log_data

    def test_json_formatter_with_exception(self):
        """Test JSON formatting with exception information."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/app/test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )
        record.module = "test"
        record.funcName = "test_function"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "exception" in log_data
        assert "ValueError: Test exception" in log_data["exception"]

    def test_json_formatter_with_user_id(self):
        """Test JSON formatting with custom user_id field."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/app/test.py",
            lineno=20,
            msg="User action",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"
        record.user_id = 123

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["user_id"] == 123

    def test_json_formatter_with_product_id(self):
        """Test JSON formatting with custom product_id field."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/app/test.py",
            lineno=20,
            msg="Product scraped",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"
        record.product_id = 456

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["product_id"] == 456

    def test_json_formatter_with_request_id(self):
        """Test JSON formatting with custom request_id field."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/app/test.py",
            lineno=20,
            msg="Request processed",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"
        record.request_id = "req-789"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["request_id"] == "req-789"


@pytest.mark.unit
class TestSetupLogging:
    """Test suite for setup_logging function."""

    def test_setup_logging_console_only(self):
        """Test logging setup with console handler only."""
        setup_logging(log_level="INFO", log_dir=None, enable_json=False)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 1

        # Check console handler exists
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) >= 1

    def test_setup_logging_with_json_format(self):
        """Test logging setup with JSON formatting."""
        setup_logging(log_level="DEBUG", log_dir=None, enable_json=True)

        root_logger = logging.getLogger()
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]

        assert len(console_handlers) >= 1
        # Check that formatter is JSONFormatter
        assert isinstance(console_handlers[0].formatter, JSONFormatter)

    def test_setup_logging_with_file_rotation(self):
        """Test logging setup with file rotation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(log_level="INFO", log_dir=temp_dir, enable_json=False, enable_rotation=True)

            root_logger = logging.getLogger()

            # Check that log files were created
            log_path = Path(temp_dir)
            # Note: Files may not exist until first log write

            # Check handlers
            file_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.handlers.TimedRotatingFileHandler)
            ]
            assert len(file_handlers) >= 1

    def test_setup_logging_with_json_and_files(self):
        """Test logging setup with JSON formatting and file handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(log_level="INFO", log_dir=temp_dir, enable_json=True, enable_rotation=True)

            root_logger = logging.getLogger()

            # Check file handlers exist
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) >= 1

            # Check that at least one uses JSON formatter
            has_json_formatter = any(isinstance(h.formatter, JSONFormatter) for h in file_handlers)
            assert has_json_formatter

    def test_setup_logging_without_rotation(self):
        """Test logging setup without file rotation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            setup_logging(log_level="INFO", log_dir=temp_dir, enable_json=False, enable_rotation=False)

            root_logger = logging.getLogger()
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]

            # Should have file handler but not rotating file handler
            assert any(
                isinstance(h, logging.FileHandler) and not isinstance(h, logging.handlers.TimedRotatingFileHandler)
                for h in root_logger.handlers
            )

    def test_setup_logging_creates_log_directory(self):
        """Test that setup_logging creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs" / "app"
            assert not log_dir.exists()

            setup_logging(log_level="INFO", log_dir=str(log_dir), enable_json=False)

            assert log_dir.exists()

    def test_setup_logging_third_party_loggers_suppressed(self):
        """Test that third-party library loggers are set to WARNING level."""
        setup_logging(log_level="DEBUG", log_dir=None, enable_json=False)

        # Check that noisy loggers are suppressed
        assert logging.getLogger("urllib3").level == logging.WARNING
        assert logging.getLogger("requests").level == logging.WARNING
        assert logging.getLogger("sqlalchemy.engine").level == logging.WARNING
        assert logging.getLogger("celery").level == logging.INFO


@pytest.mark.unit
class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test.module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_different_names(self):
        """Test that different names return different loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 != logger2


@pytest.mark.unit
class TestLogContext:
    """Test suite for LogContext context manager."""

    def test_log_context_adds_extra_fields(self):
        """Test that LogContext adds extra fields to log records."""
        logger = get_logger("test.context")
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        with LogContext(logger, user_id=123, request_id="req-456"):
            record = logging.LogRecord(
                name="test.context",
                level=logging.INFO,
                pathname="/app/test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            record.module = "test"
            record.funcName = "test_func"

            # The factory should add extra fields
            factory = logging.getLogRecordFactory()
            new_record = factory(
                name="test.context",
                level=logging.INFO,
                pathname="/app/test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            assert hasattr(new_record, "user_id")
            assert hasattr(new_record, "request_id")
            assert new_record.user_id == 123
            assert new_record.request_id == "req-456"

    def test_log_context_restores_factory(self):
        """Test that LogContext restores original factory on exit."""
        logger = get_logger("test.restore")
        old_factory = logging.getLogRecordFactory()

        with LogContext(logger, user_id=999):
            # Inside context, factory should be different
            context_factory = logging.getLogRecordFactory()
            assert context_factory != old_factory

        # After context, factory should be restored
        restored_factory = logging.getLogRecordFactory()
        assert restored_factory == old_factory
