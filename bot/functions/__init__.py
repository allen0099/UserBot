import asyncio
import inspect
from typing import Any

from pyrogram import raw, types
from pyrogram.enums import ChatType

from bot.enums import EmojiList
from bot.functions.links import (
    get_chat_link,
    get_message_link,
    get_sticker_set_link,
)


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


def get_sticker_pack_info(
    pyrogram_sticker: types.Sticker, sticker: raw.types.StickerSet
) -> str:
    return (
        f"貼圖包連結：{get_sticker_set_link(sticker)}\n"
        f"貼圖高度：<code>{pyrogram_sticker.height}</code>\n"
        f"貼圖寬度：<code>{pyrogram_sticker.width}</code>\n"
        f"影片貼圖：{EmojiList.TRUE if pyrogram_sticker.is_video else EmojiList.FALSE}\n"
        f"動態貼圖：{EmojiList.TRUE if pyrogram_sticker.is_animated else EmojiList.FALSE}\n"
    )


def capitalize(s: str, _all: bool = False) -> str:
    if not _all:
        new_append: list[str] = s.capitalize().split("_")

    else:
        appended: list[str] = s.split("_")
        new_append: list[str] = [_.capitalize() for _ in appended]

    return " ".join(new_append)


def get_mute_permission() -> types.ChatPermissions:
    permission: types.ChatPermissions = types.ChatPermissions()

    permissions: list[tuple[str, Any]] = [
        member
        for member in inspect.getmembers(permission)
        if not member[0].startswith("_")
        and not inspect.isfunction(member[1])
        and not inspect.ismethod(member[1])
    ]

    for p in permissions:
        setattr(permission, p[0], False)

    return permission


async def msg_auto_clean(msg: types.Message, time: int = 10):
    await asyncio.sleep(time)
    await msg.delete()
