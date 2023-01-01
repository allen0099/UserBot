import logging

from core.log import main_logger
from .domain import DomainBlacklist
from .fullname import FullNameBlacklist
from .word import WordBlacklist

log: logging.Logger = main_logger(__name__)
