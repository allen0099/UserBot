import logging

from pyrogram import types
from pyrogram.enums import MessageMediaType

from bot.validation import BaseRule
from core import main_logger
from core.log import event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


class EditedRule(BaseRule):
    """是否為編輯過的訊息。"""

    name: str = "編輯訊息"

    def update_error_message(self) -> None:
        self.error_message: str = "使用者於 {time} 編輯訊息。".format(
            time=self.msg.edit_date.strftime("%Y-%m-%d %H:%M:%S")
        )

    def is_violate_rule(self) -> bool:
        if self.msg.edit_date:
            return True
        return False


class ForwardRule(BaseRule):
    """是否為轉發訊息。"""

    name: str = "黑名單轉發"

    def update_error_message(self) -> None:
        forward_target: types.User | types.Chat | None = (
            self.msg.forward_from or self.msg.forward_from_chat
        )
        self.error_message: str = "使用者轉發黑名單訊息：{id}。".format(id=forward_target.id)

    def is_violate_rule(self) -> bool:
        if self.msg.forward_date:
            # TODO: 黑名單檢查
            return True
        return False


class URLRule(BaseRule):
    """是否為含有網址的訊息。"""

    name = "黑名單網址"
    error_message: str = "發送包含黑名單網址的訊息 {url}。"

    def parse_url(self):
        """Fetch all possible URLs from the message.
        1. Parse the message from webpage preview.
        2. Parse the message from entities. -> split
        """
        if self.msg.web_page and self.msg.web_page.type in [
            "telegram_user",
            "telegram_bot",
            "telegram_channel",
            "telegram_megagroup",
        ]:
            # TODO: Validate the mentioned data is not in blacklist
            pass

    def mask_url(self):
        """Mask the URL that may be a harmful link."""
        pass

    def is_violate_rule(self) -> bool:
        pass


class StickerRule(BaseRule):
    """是否為貼圖。"""

    name: str = "貼圖"

    def update_error_message(self) -> None:
        self.error_message: str = "發送貼圖 name={name}。".format(
            name=self.msg.sticker.set_name
        )

    def is_violate_rule(self) -> bool:
        if self.msg.sticker:
            return True
        return False


class ViaBotRule(BaseRule):
    """是否透過機器人發送訊息。"""

    name: str = "Inline Bot"

    def update_error_message(self) -> None:
        self.error_message: str = "使用者透過機器人 id={id} 發送訊息。".format(
            id=self.msg.via_bot.id
        )

    def is_violate_rule(self) -> bool:
        if self.msg.via_bot:
            # TODO: 黑名單檢查
            return True
        return False


class MediaRule(BaseRule):
    """是否為媒體訊息。"""

    name: str = "媒體訊息"

    def update_error_message(self) -> None:
        self.error_message: str = "發送 {type} 訊息。".format(type=self.msg.media)

    def is_violate_rule(self) -> bool:
        if self.msg.media and self.msg.media in [
            MessageMediaType.PHOTO,
            MessageMediaType.VIDEO,
        ]:
            # TODO: pic, video
            return True
        return False


class MediaGroupRule(BaseRule):
    """是否為媒體群組。"""

    name: str = "媒體群組"

    def update_error_message(self) -> None:
        self.error_message: str = "發送媒體群組 {group_id}。".format(
            group_id=self.msg.media_group_id
        )

    def is_violate_rule(self) -> bool:
        if self.msg.media_group_id:
            # TODO: 檢查此媒體群組的[所有訊息]
            #  需要檢查所有訊息內的第一條 id 是否是入群後的第一次發言，如果是則拋出錯誤

            # TODO: 實作簡易的相同群組內的同媒體群組的中斷，避免重複檢查相同媒體群組
            #  可以用 tuple 放在 class 儲存區內，檢查 tuple 是否已存在
            #  如存在則拋出另一種的錯誤，中斷訊息檢查

            # TODO: 新訊息進來時，檢查已經存在的 tuple 是否還在有效期內 (15 秒)
            #  沒有的話則將 tuple 清除
            return True
        return False


class EntityRule(BaseRule):
    """是否為含有實體的訊息。"""

    name: str = "實體訊息"

    def update_error_message(self) -> None:
        self.error_message = "發送含有實體的訊息 {entities}。".format(entities=self.msg.entities)

    def is_violate_rule(self) -> bool:
        if self.msg.entities:
            # TODO: 1. mention check
            #  2. URL check
            #  3. premium sticker id black list
            return True
        return False


class LinkedChatRule(BaseRule):
    """是否為連結群組。"""

    name: str = "連結群組"
