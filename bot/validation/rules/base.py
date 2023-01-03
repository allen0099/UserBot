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
        self.error_message: str = "<unset>"

    def update_error_message(self) -> None:
        raise NotImplementedError

    def is_violate_rule(self) -> bool:
        """Return True if the message violates the rule."""
        raise NotImplementedError

    def run_validate(self):
        if self.is_violate_rule():
            self.update_error_message()
            raise RuleViolated(self.name, self.error_message)


class MessageRule(BaseRule, ABC):
    """The basic rule for all validation rules."""

    name: str = "預設訊息規則"

    def __init__(self):
        super().__init__()
        self.msg: types.Message | None = None
        self.target: types.User | types.Chat | None = None

    def run_validate(
        self, *, msg: types.Message = None, target: types.User | types.Chat = None
    ) -> None:
        if not msg:
            raise ValueError("Must provide message to check.")

        if not target:
            raise ValueError("Must provide target to check.")

        self.msg = msg
        self.target = target

        super().run_validate()


class UserRule(BaseRule, ABC):
    """Message contain blacklisted sender or content."""

    name: str = "預設使用者規則"

    def __init__(self):
        super().__init__()
        self.user: types.User | None = None

    def run_validate(self, *, user: types.User = None) -> None:
        if not user:
            raise ValueError("Must provide user to check.")

        self.user = user

        super().run_validate()
