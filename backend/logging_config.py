"""
Logging configuration using structlog with rotating file output.
Call setup_logging() once at application startup.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

import structlog

_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "app.log"


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configures structlog + stdlib logging.
    - Console: human-readable colored output
    - File: JSON structured logs, rotating at 10 MB, keeping 5 backups
    """
    _LOG_DIR.mkdir(exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)

    # --- File handler (JSON, rotating) ---
    file_handler = logging.handlers.RotatingFileHandler(
        _LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)

    # --- Console handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Configure stdlib root logger to feed into both handlers
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler],
        force=True,
    )

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "uvicorn.access", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Shared processors for all structlog loggers
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
    ]

    # File renderer — always JSON
    file_renderer = structlog.processors.JSONRenderer()

    # Console renderer — colored if interactive, plain JSON if log_format == "json"
    if log_format == "json" or not sys.stdout.isatty():
        console_renderer = structlog.processors.JSONRenderer()
    else:
        console_renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Attach structlog formatter to each handler
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=file_renderer,
            foreign_pre_chain=shared_processors,
        )
    )
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=console_renderer,
            foreign_pre_chain=shared_processors,
        )
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Returns a structlog logger bound to the given name."""
    return structlog.get_logger(name)
