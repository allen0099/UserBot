import logging
from datetime import datetime, timedelta
from typing import Type

from pyrogram import types

from bot.errors import RuleViolated
from bot.validation.rules import (
    BaseRule,
    BlacklistUserChecker,
    FullnameChecker,
    ThirdPartyChecker,
)
from bot.validation.rules.message import (
    EditedRule,
    ForwardRule,
    MediaGroupRule,
    MediaRule,
    StickerRule,
    URLRule,
    ViaBotRule,
)
from core import main_logger
from core.log import event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class BaseValidator:
    """The basic validator for all validation rules."""

    media_group_map: dict[int, dict[str, str | datetime]] = {
        -100100100: {"mg_id": "0", "timestamp": datetime.now()}
    }

    def __init__(self, msg: types.Message, _rules: list[Type[BaseRule]] = None) -> None:
        self.message: types.Message = msg
        self.from_chat: types.Chat = msg.chat
        self.target: types.User | types.Chat | None = msg.from_user or msg.sender_chat

        self.errors: list[str] = []
        self.error_messages: dict[str, ...] = {}

        if not _rules:
            self.rules: list[Type[BaseRule]] = self.get_rules()
        else:
            self.rules: list[Type[BaseRule]] = _rules

    def __md_group_clean_up(self):
        """Clean up media group map."""
        for chat_id, value in BaseValidator.media_group_map.items():
            if datetime.now() - value.get("timestamp") > timedelta(minutes=5):
                del BaseValidator.media_group_map[chat_id]

    def get_rules(self) -> list[Type[BaseRule]]:
        raise NotImplementedError

    def validate(self, raise_error: bool = False) -> bool:
        """Return True if the message passes all rules."""
        for rule in self.rules:
            try:
                rule().is_valid(msg=self.message, target=self.target)
            except RuleViolated as error:
                self.errors.append(rule.__name__)
                self.error_messages[error.name] = error.detail

        if self.message.media_group_id:
            current: dict[str, str | datetime] = BaseValidator.media_group_map.get(
                self.from_chat.id
            )
            if current:
                if self.message.media_group_id == current.get(
                    "mg_id"
                ) and datetime.now() - current.get("timestamp") < timedelta(seconds=10):
                    self.errors.clear()
                    self.error_messages.clear()

                    return True

            BaseValidator.media_group_map[self.from_chat.id] = {
                "mg_id": self.message.media_group_id,
                "timestamp": datetime.now(),
            }

        if raise_error and self.errors:
            raise RuleViolated("Contain errors", "\n".join(self.errors))

        self.__md_group_clean_up()
        return not self.errors


class MessageValidator(BaseValidator):
    def get_rules(self) -> list[Type[BaseRule]]:
        # TODO(dev): Let group decide which rules to use.
        return [
            ForwardRule,
            MediaRule,
            MediaGroupRule,
            StickerRule,
            ViaBotRule,
            URLRule,
            EditedRule,
        ]


class UserValidator(BaseValidator):
    def get_rules(self) -> list[Type[BaseRule]]:
        return [BlacklistUserChecker, FullnameChecker, ThirdPartyChecker]
