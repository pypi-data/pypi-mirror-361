"""Logging utilities for pyagentai."""

import logging
import os
import sys
from logging import handlers

import structlog

from pyagentai.utils.text_processor import sanitize_text

# Get environment variables with defaults
LOG_LEVEL = os.getenv("AGENTAI_LOG_LEVEL")
LOG_FORMAT = os.getenv("AGENTAI_LOG_FORMAT")
LOG_DIR = os.getenv("AGENTAI_LOG_DIR")
LOG_FILE_ENABLED = os.getenv("AGENTAI_LOG_FILE_ENABLED")
LOG_CONSOLE_ENABLED = os.getenv("AGENTAI_LOG_CONSOLE_ENABLED")
LOG_ROTATE_WHEN = os.getenv("AGENTAI_LOG_ROTATE_WHEN")
LOG_ROTATE_BACKUP = os.getenv("AGENTAI_LOG_ROTATE_BACKUP")

# A mapping of log level strings to their numeric values
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def initialize_logging(
    log_level: str | None = None,
    log_format: str | None = None,
    log_dir: str | None = None,
    log_file_enabled: bool | None = None,
    log_file_name: str | None = None,
    log_console_enabled: bool | None = None,
    log_rotate_when: str | None = None,
    log_rotate_backup: int | None = None,
) -> None:
    """Initialize logging for pyagentai.

    This function configures structlog for the package. It can be customized
    with various parameters, or it will use environment variables/defaults.

    Args:
        log_level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: The log format (json or console).
        log_dir: The directory to store log files.
        log_file_enabled: Whether to log to files.
        log_file_name: The name of the log file.
        log_console_enabled: Whether to log to the console.
        log_rotate_when: When to rotate logs (see TimedRotatingFileHandler).
        log_rotate_backup: Number of backup logs to keep.

    Returns:
        None
    """
    # Remove any previously added pyagentai handlers.
    root_logger = logging.getLogger("pyagentai")
    for handler in root_logger.handlers[:]:
        if getattr(handler, "_pyagentai_managed", False):
            root_logger.removeHandler(handler)

    # Use provided values or environment variables/defaults
    level = log_level or LOG_LEVEL or "INFO"
    level_num = LOG_LEVEL_MAP.get(level.upper(), logging.INFO)
    format_type = log_format or LOG_FORMAT or "console"
    directory = log_dir or LOG_DIR or "logs"
    rotate_when = log_rotate_when or LOG_ROTATE_WHEN or "W6"

    if log_file_enabled is not None:
        file_enabled = log_file_enabled
    elif LOG_FILE_ENABLED is not None:
        file_enabled = LOG_FILE_ENABLED.lower() == "true"
    else:
        file_enabled = False  # default to false

    if log_console_enabled is not None:
        console_enabled = log_console_enabled
    elif LOG_CONSOLE_ENABLED is not None:
        console_enabled = LOG_CONSOLE_ENABLED.lower() == "true"
    else:
        console_enabled = True  # default to true

    if log_rotate_backup is not None:
        rotate_backup = log_rotate_backup
    elif LOG_ROTATE_BACKUP is not None:
        rotate_backup = int(LOG_ROTATE_BACKUP)
    else:
        rotate_backup = 4  # default to 4

    # Create handlers list
    handlers_list = []

    # Set up console logging if enabled
    if console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level_num)
        setattr(console_handler, "_pyagentai_managed", True)  # noqa: B010
        handlers_list.append(console_handler)

    # Set up file logging if enabled
    if file_enabled:
        # Create log directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Use provided file name or default to 'pyagentai'
        file_name = sanitize_text(log_file_name or "pyagentai")

        # Configure file handler with rotation
        log_file_path = f"{directory}/{file_name}.log"
        file_handler = handlers.TimedRotatingFileHandler(
            filename=log_file_path,
            when=rotate_when,
            backupCount=int(rotate_backup),
            encoding="utf-8",
        )
        file_handler.setLevel(level_num)
        setattr(file_handler, "_pyagentai_managed", True)  # noqa: B010
        handlers_list.append(file_handler)  # type: ignore

    # Configure root logger
    if handlers_list:
        root_logger.setLevel(level_num)
        for handler in handlers_list:
            root_logger.addHandler(handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.UnicodeDecoder(),
            # Choose renderer based on format type
            structlog.processors.JSONRenderer()
            if format_type.lower() == "json"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _auto_configure_if_env_vars_set() -> None:
    """Check for AGENTAI env vars and configure logging if any are present."""
    env_vars_to_check = [
        LOG_LEVEL,
        LOG_FORMAT,
        LOG_DIR,
        LOG_FILE_ENABLED,
        LOG_CONSOLE_ENABLED,
        LOG_ROTATE_WHEN,
        LOG_ROTATE_BACKUP,
    ]
    if any(env_vars_to_check):
        initialize_logging()
    else:
        # remove all logging handlers for pyagentai
        root_logger = logging.getLogger("pyagentai")
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.addHandler(logging.NullHandler())

        # configure structlog with AsyncBoundLogger
        structlog.configure(
            wrapper_class=structlog.stdlib.AsyncBoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


# Initialize logging with default settings when this module is imported,
# but only if environment variables are set.
_auto_configure_if_env_vars_set()
