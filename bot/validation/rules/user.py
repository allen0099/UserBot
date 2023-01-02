import logging
import re
from abc import ABC
from html import escape
from re import Pattern

from pyrogram import types

from bot.enums import PermissionLevel
from bot.validation.rules import BlackListRule
from core import main_logger
from core.log import event_logger
from database import db
from database.models.blacklist import FullNameBlacklist
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class BlacklistUserChecker(BlackListRule):
    """訊息傳送自黑名單使用者。"""

    name = "黑名單使用者"
    table = Users

    def is_blacklisted(self, id: int) -> bool:
        q: Users | None = (
            db.session.query(self.table)
            .filter_by(id=id, level=PermissionLevel.BLACK)
            .first()
        )
        return True if q else False

    def is_violate_rule(self) -> bool:
        if self.is_blacklisted(self.target.id):
            return False
        return True


class FullnameChecker(BlackListRule, ABC):
    """使用者名稱包含禁字。"""

    name = "使用者名稱"
    table = FullNameBlacklist

    def get_pattern(self) -> Pattern:
        word: list[FullNameBlacklist] = (
            db.session.query(self.table).filter_by(disabled=False).all()
        )

        if not word:
            # return a pattern that will never match
            return re.compile(r"^\b\B$")

        pattern: str = "^.*(?:" + "|".join([f"{w.word}" for w in word]) + ").*$"

        return re.compile(pattern)

    def is_violate_rule(self) -> bool:
        if isinstance(self.target, types.User):
            full_name: str = f"{self.target.first_name} {self.target.last_name or ''}"

        else:
            full_name: str = self.target.title

        return self.get_pattern().match(escape(full_name).strip()) is None


class ThirdPartyChecker(BlackListRule, ABC):
    """第三方串接檢查。"""

    name = "第三方串接"

    def combot_cas_banned(self) -> bool:
        # TODO: @cas_discussion in 10/24 issue
        self.__doc__ = "使用者被 Combot CAS 系統封鎖。\nhttps://cas.chat/query?u={id}"
        return False

    def is_violate_rule(self) -> bool:
        if self.combot_cas_banned():
            return False

        return True
