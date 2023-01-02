import logging

from bot.validation.rules.base import BlackListRule, BaseRule
from core import main_logger
from core.log import event_logger
from .user import BlacklistUserChecker, FullnameChecker, ThirdPartyChecker

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)
