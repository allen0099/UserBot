import logging
from datetime import datetime, timedelta
from typing import Type

from pyrogram import types

from bot.errors import RuleViolated
from bot.validation.rules import (
    BlacklistUserRule,
    MessageRule,
    NameRule,
    ThirdPartyRule,
)
from bot.validation.rules.base import BaseRule, UserRule
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

    def get_rules(self) -> list[Type[MessageRule]]:
        raise NotImplementedError

    def validate(self, raise_error: bool = False) -> bool:
        """Return True if the message passes all rules."""
        raise NotImplementedError


class MessageValidator(BaseValidator):
    media_group_map: dict[int, dict[str, str | datetime]] = {
        -100100100: {"mg_id": "0", "timestamp": datetime.now()}
    }

    def __init__(
        self, msg: types.Message, _rules: list[Type[MessageRule]] = None
    ) -> None:
        self.message: types.Message = msg
        self.from_chat: types.Chat = msg.chat
        self.target: types.User | types.Chat | None = msg.from_user or msg.sender_chat

        self.errors: list[str] = []
        self.error_messages: dict[str, ...] = {}

        if not _rules:
            self.rules: list[Type[MessageRule]] = self.get_rules()
        else:
            self.rules: list[Type[MessageRule]] = _rules

    @staticmethod
    def __md_group_clean_up():
        """Clean up media group map."""
        for chat_id, value in MessageValidator.media_group_map.items():
            if datetime.now() - value.get("timestamp") > timedelta(minutes=5):
                del MessageValidator.media_group_map[chat_id]

    def validate(self, raise_error: bool = False) -> bool:
        """Return True if the message passes all rules."""
        for rule in self.rules:
            try:
                rule().run_validate(msg=self.message, target=self.target)
            except RuleViolated as error:
                self.errors.append(rule.__name__)
                self.error_messages[error.name] = error.detail

        if self.message.media_group_id:
            current: dict[str, str | datetime] = MessageValidator.media_group_map.get(
                self.from_chat.id
            )
            if current:
                if self.message.media_group_id == current.get(
                    "mg_id"
                ) and datetime.now() - current.get("timestamp") < timedelta(seconds=10):
                    self.errors.clear()
                    self.error_messages.clear()

                    return True

            MessageValidator.media_group_map[self.from_chat.id] = {
                "mg_id": self.message.media_group_id,
                "timestamp": datetime.now(),
            }

        if raise_error and self.errors:
            raise RuleViolated("Contain errors", "\n".join(self.errors))

        self.__md_group_clean_up()
        return not self.errors

    def get_rules(self) -> list[Type[MessageRule]]:
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
    # Known issue: user approved by admin will not get any service message,
    # instead, bot will get a normal message which only contain message id, user, chat, and date.

    # WARNING: If group enabled participants_hidden, will not get any service message.

    def __init__(self, user: types.User, _rules: list[Type[UserRule]] = None) -> None:
        self.user: types.User = user

        self.errors: list[str] = []
        self.error_messages: dict[str, ...] = {}

        if not _rules:
            self.rules: list[Type[UserRule]] = self.get_rules()
        else:
            self.rules: list[Type[UserRule]] = _rules

    def validate(self, raise_error: bool = False) -> bool:
        for rule in self.rules:
            try:
                rule().run_validate(user=self.user)
            except RuleViolated as error:
                self.errors.append(rule.__name__)
                self.error_messages[error.name] = error.detail

        if raise_error and self.errors:
            raise RuleViolated("Contain errors", "\n".join(self.errors))

        return not self.errors

    def get_rules(self) -> list[Type[UserRule]]:
        return [BlacklistUserRule, ThirdPartyRule]
