import asyncio
import warnings
from typing import Optional

from pyrogram import Client, errors
from pyrogram import types
from pyrogram.enums import ChatType

from bot.functions.links import get_chat_link, get_message_link


def get_user_info(user: types.User) -> str:
    call_sign: str = "機器人" if user.is_bot else "使用者"
    return f"{call_sign}：{user.mention}\n{call_sign} ID：<code>{user.id}</code>\n"


def get_chat_info(chat: types.Chat) -> str:
    call_sign: str = "頻道" if chat.type is ChatType.CHANNEL else "群組"
    return f"{call_sign}：{get_chat_link(chat)}\n{call_sign} ID：<code>{chat.id}</code>\n"


def get_message_info(chat: types.Chat, message_id: int) -> str:
    return (
        f"原始訊息 ID：<code>{message_id}</code>\n"
        f"原始訊息連結：{get_message_link(chat, message_id)}\n"
    )


async def get_common_chats(cli: Client, uid: int) -> list[types.Chat]:
    warnings.warn("This function is deprecated.", DeprecationWarning)

    inviter_commons: Optional[list[types.Chat]] = None
    times = 1
    while not inviter_commons:
        try:
            inviter_commons = await cli.get_common_chats(uid)
        except errors.PeerIdInvalid:
            times += 1
            if times >= 5:
                raise ValueError("Max retries exceeded!")
            log.debug(
                f"Can't get common chats with {uid}, this is {times} times try..."
            )
            await asyncio.sleep(5)
        return inviter_commons


def capitalize(s: str, _all: bool = False) -> str:
    if not _all:
        new_append: list[str] = s.capitalize().split("_")

    else:
        appended: list[str] = s.split("_")
        new_append: list[str] = [_.capitalize() for _ in appended]

    return " ".join(new_append)
