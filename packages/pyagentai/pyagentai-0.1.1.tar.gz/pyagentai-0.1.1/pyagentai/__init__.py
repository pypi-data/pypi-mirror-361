"""A Python library for seamless integration with Agent.ai APIs."""


from pyagentai.client import AgentAIClient
from pyagentai.config.agentai_config import AgentAIConfig
from pyagentai.config.agentai_endpoints import AgentAIEndpoints
from pyagentai.utils.logger import initialize_logging

__version__ = "0.1.1"

__all__ = ["AgentAIClient", "AgentAIConfig", "AgentAIEndpoints"]


def configure_logging(
    log_level: str | None = None,
    log_format: str | None = None,
    log_file_enabled: bool | None = None,
    log_file_name: str | None = None,
    log_dir: str | None = None,
) -> None:
    """Configure logging for the pyagentai package.
    Use this function or set environment variables to configure logging.

    ENV VARS:
        AGENTAI_LOG_LEVEL
        AGENTAI_LOG_FORMAT
        AGENTAI_LOG_DIR
        AGENTAI_LOG_FILE_ENABLED
        AGENTAI_LOG_CONSOLE_ENABLED
        AGENTAI_LOG_ROTATE_WHEN
        AGENTAI_LOG_ROTATE_BACKUP

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or console)
        log_file_enabled: Whether to log to files
        log_file_name: Name for the log file
        log_dir: Directory for log files

    Returns:
        None
    """
    initialize_logging(
        log_level=log_level,
        log_format=log_format,
        log_file_enabled=log_file_enabled,
        log_file_name=log_file_name,
        log_dir=log_dir,
    )
