import logging
import re
from html import escape
from re import Pattern

import requests
from requests import Response

from bot.enums import PermissionLevel
from bot.validation.rules import UserRule
from core import main_logger
from core.log import event_logger
from database import db
from database.models.blacklist import FullNameBlacklist
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class BlacklistUserRule(UserRule):
    """訊息傳送自黑名單使用者。"""

    name = "黑名單使用者"

    def update_error_message(self) -> None:
        self.error_message = f"使用者 {self.user.id} 在黑名單中。"

    def is_violate_rule(self) -> bool:
        q: Users | None = (
            db.session.query(Users)
            .filter_by(id=self.user.id, level=PermissionLevel.BLACK)
            .first()
        )
        return True if q else False


class NameRule(UserRule):
    """使用者名稱包含禁字。"""

    name = "使用者名稱"

    def get_pattern(self) -> Pattern:
        word: list[FullNameBlacklist] = (
            db.session.query(FullNameBlacklist).filter_by(disabled=False).all()
        )

        if not word:
            # return a pattern that will never match
            return re.compile(r"^\b\B$")

        pattern: str = "^.*(?:" + "|".join([f"{w.word}" for w in word]) + ").*$"

        return re.compile(pattern)

    def is_violate_rule(self) -> bool:
        full_name: str = f"{self.user.first_name} {self.user.last_name or ''}"

        return self.get_pattern().match(escape(full_name).strip()) is None


class ThirdPartyRule(UserRule):
    """第三方串接檢查。"""

    name = "第三方串接"

    def __init__(self):
        super().__init__()
        self.reason: str = ""
        self.additional: str = ""

    def update_error_message(self) -> None:
        match self.reason.lower():
            case "cas":
                self.error_message = (
                    f"使用者被 Combot CAS 系統封鎖。\nhttps://cas.chat/query?u={self.user.id}"
                )

            case "husky":
                self.error_message = (
                    f"使用者被 Husky 系統封鎖。\n"
                    f"https://husky.moe/check?id={self.user.id}\n"
                    f"附加資訊：{self.additional}"
                )

            case _:
                self.error_message = f"使用者被第三方系統封鎖。\n"

    def combot_cas_banned(self) -> bool:
        try:
            r: Response = requests.get(f"https://api.cas.chat/check?user_id={self.user.id}")

        except requests.exceptions.ConnectionError as e:
            log.error(f"Combot CAS API error: ConnectionError, {e}")
            return False


        if r.ok:
            response: dict[str, ...] = r.json()

            if response.get("ok", False):
                return True

        else:
            log.error(f"Combot CAS API error: {r.status_code} {r.reason}")

        return False

    def husky_banned(self) -> bool:
        try:
            r: Response = requests.get(f"https://husky.moe/check?id={self.user.id}")

        except requests.exceptions.ConnectionError as e:
            log.error(f"Husky API error: ConnectionError, {e}")
            return False

        if r.ok:
            response: dict[str, ...] = r.json()

            if response.get("is_banned", False):
                self.additional = response.get("tag", "")
                return True

        else:
            log.error(f"Husky API error: {r.status_code} {r.reason}")

        return False

    def is_violate_rule(self) -> bool:
        if self.combot_cas_banned():
            self.reason = "cas"
            return True

        if self.husky_banned():
            self.reason = "husky"
            return True

        return False
