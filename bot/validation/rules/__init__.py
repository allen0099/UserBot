import logging

from bot.validation.rules.base import UserRule, MessageRule
from core import main_logger
from core.log import event_logger
from .user import BlacklistUserRule, NameRule, ThirdPartyRule

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)
