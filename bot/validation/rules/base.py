import logging
from abc import ABC

from pyrogram import types

from bot.errors import RuleViolated
from core import main_logger
from core.log import event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class BaseRule:
    """The basic rule for all validation rules."""

    name: str = "預設規則"

    def __init__(self):
        self._error_message: str = "<unset>"
        self.msg: types.Message | None = None
        self.target: types.User | types.Chat | None = None

    @property
    def error_message(self) -> str:
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        self._error_message = value

    def update_error_message(self) -> None:
        raise NotImplementedError

    def is_violate_rule(self) -> bool:
        """Return True if the message violates the rule."""
        raise NotImplementedError

    def is_valid(
        self, msg: types.Message = None, target: types.User | types.Chat = None
    ) -> None:
        assert msg is not None, "Must provide message to check."
        assert target is not None, "Must provide target to check."

        self.msg = msg
        self.target = target

        if self.is_violate_rule():
            self.update_error_message()
            raise RuleViolated(self.name, self.error_message)


class BlackListRule(BaseRule, ABC):
    """Message contain blacklisted sender or content."""

    table = None

    def is_blacklisted(self, id: int) -> bool:
        raise NotImplementedError
