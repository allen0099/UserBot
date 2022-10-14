import logging

from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)

COMMAND_PREFIXES: list[str] = ["!", "$"]
