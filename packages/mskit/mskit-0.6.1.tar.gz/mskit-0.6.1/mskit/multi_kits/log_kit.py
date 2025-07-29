import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Literal, Optional, Union

LoggerHandleFormats = {
    "generic": "[%(asctime)s]-[%(name)s]-[%(levelname)s] %(message)s",
    "generic_plus_fromline": "[%(asctime)s]-[%(name)s]-[%(levelname)s] %(message)s \t[%(filename)s:%(lineno)d]",
    "generic_plus_pid_tid": "[%(asctime)s]-[%(name)s]-[%(levelname)s]-[%(processName)s:%(process)d]-[%(threadName)s:%(thread)d] %(message)s",
    "generic_plus_fromline_pid_tid": "[%(asctime)s]-[%(name)s]-[%(levelname)s]-[%(processName)s:%(process)d]-[%(threadName)s:%(thread)d] %(message)s \t[%(filename)s:%(lineno)d]",
}


def console_file_logger(
    logger_name: str = "root",
    log_path: Optional[Union[str, Path]] = None,
    log_console_level: Optional[int] = None,
    log_file_level: Optional[int] = None,
    log_console_format: Literal[
        "generic",
        "generic_plus_fromline",
        "generic_plus_pid_tid",
        "generic_plus_fromline_pid_tid",
    ] = "generic",
    log_file_format: str = "generic_plus_fromline",
    date_fmt: str = "%Y-%m-%d %H:%M:%S",
    write_init_logs: bool = False,
    reset_handlers: bool = True,
    use_rich_handler: bool = False,
) -> logging.Logger:
    """
    TODO: custom init messages
    TODO: multi log handlers
    Setup a logger with name `logger_name` and store in `log_path` if path is defined
    """
    logger = logging.getLogger(logger_name)

    if len(logger.handlers) > 0:
        if reset_handlers:
            for h in logger.handlers:
                logger.removeHandler(h)
        else:
            return logger

    start_time = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    if log_console_level is None:
        log_console_level = os.environ.get(f"{logger_name.upper()}_LOG_LEVEL", "INFO")
    if log_console_format is None:
        log_console_format = "generic_plus_fromline"
    if log_console_format in LoggerHandleFormats:
        log_console_format = LoggerHandleFormats.get(log_console_format, log_console_format)
    stored_msgs = [
        f'Logger "{logger_name}" created at {start_time}',
        f'Logger "{logger_name}" has level (console): "{log_console_level}"',
        f'Logger "{logger_name}" has format (console): "{log_console_format}"',
    ]

    logger.setLevel(log_console_level)

    if use_rich_handler:
        from rich.logging import RichHandler

        stdout_handler = RichHandler()
    else:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(log_console_format, date_fmt)
    stdout_handler.setLevel(log_console_level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if log_path is not None:
        file_handler = logging.FileHandler(log_path)

        if log_file_level is None:
            log_file_level = log_console_level
        file_handler.setLevel(log_file_level)

        if log_file_format is None:
            log_file_format = log_console_format
        else:
            log_file_format = LoggerHandleFormats.get(log_file_format, log_file_format)
        formatter = logging.Formatter(log_file_format, date_fmt)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stored_msgs.extend(
            [
                f"Set store path of logger {logger_name} to: {log_path}",
                f'Logger "{logger_name}" has level (file): "{log_file_level}"',
                f'Logger "{logger_name}" has format (file): "{log_file_format}"',
            ]
        )

    if write_init_logs:
        for msg in stored_msgs:
            logger.info(msg)

    return logger


def get_logger(logger, **kws):
    pass
