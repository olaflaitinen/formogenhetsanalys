"""Structured logging configuration using structlog.

In CI environments (detected via the CI environment variable) a JSON renderer
is used so log lines are machine-parseable. Locally a human-friendly console
renderer is used instead.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import cast

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog with appropriate renderer for the environment.

    Args:
        level: Standard logging level string (DEBUG, INFO, WARNING, ERROR).

    Examples:
        >>> configure_logging("DEBUG")
    """
    in_ci = os.getenv("CI", "").lower() in ("true", "1", "yes")

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionPrettyPrinter(),
    ]

    if in_ci:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a bound structlog logger.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        A configured structlog BoundLogger.

    Examples:
        >>> log = get_logger(__name__)
        >>> log.info("hello", key="value")
    """
    return cast("structlog.BoundLogger", structlog.get_logger(name))
