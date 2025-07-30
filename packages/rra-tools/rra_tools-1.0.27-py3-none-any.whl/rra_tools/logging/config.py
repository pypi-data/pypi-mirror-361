from __future__ import annotations

import sys
from collections.abc import Callable
from logging import Handler
from pathlib import Path
from typing import TextIO

import loguru
from loguru import logger

from rra_tools.shell_tools import mkdir

DEFAULT_LOG_MESSAGING_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level> - {extra}"
)
LOG_FORMATS = {
    # Keys are verbosity.  Specify special log formats here.
    0: ("WARNING", DEFAULT_LOG_MESSAGING_FORMAT),
    1: ("INFO", DEFAULT_LOG_MESSAGING_FORMAT),
    2: ("DEBUG", DEFAULT_LOG_MESSAGING_FORMAT),
}


def configure_logging_to_terminal(verbose: int) -> None:
    """Setup logging to sys.stdout.

    This is presumed to be one of the first calls made in an
    application entry point. Any logging that occurs before this
    call won't be intercepted or handled with the standard
    logging configuration.

    """
    logger.remove(0)  # Clear default configuration
    add_logging_sink(sys.stdout, verbose, colorize=True)


def configure_logging_to_files(log_dir: str | Path) -> None:
    """Sets up logging to a file in an output directory.

    Logs to files are done with the highest verbosity to allow
    for debugging if necessary.

    """
    mkdir(log_dir, exist_ok=True)
    add_logging_sink(
        Path(log_dir) / "main_log.json",
        verbose=3,
        serialize=True,
    )
    add_logging_sink(
        Path(log_dir) / "main_log.txt",
        verbose=3,
    )


def add_logging_sink(
    sink: TextIO | loguru.Writable | Callable[[loguru.Message], None] | Handler | Path,
    verbose: int,
    *,
    colorize: bool = False,
    serialize: bool = False,
) -> None:
    """Add a new output file handle for logging."""
    level, message_format = LOG_FORMATS.get(
        verbose, LOG_FORMATS[max(LOG_FORMATS.keys())]
    )
    logger.add(
        sink,  # type: ignore[arg-type]
        colorize=colorize,
        level=level,
        format=message_format,
        serialize=serialize,
        filter={
            # Suppress logs up to the level provided.
            "urllib3": "WARNING",  # Uselessly (for us) noisy.
        },
    )
