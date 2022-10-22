import asyncio
import inspect
from datetime import datetime, timedelta
from typing import Any

from pyrogram import raw, types
from pyrogram.enums import ChatType

from bot.enums import EmojiList
from bot.functions.links import (
    get_chat_link,
    get_message_link,
    get_sticker_set_link,
)
from core.settings import TIMEZONE


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


def capitalize(s: str, _all: bool = False) -> str:
    if not _all:
        new_append: list[str] = s.capitalize().split("_")

    else:
        appended: list[str] = s.split("_")
        new_append: list[str] = [_.capitalize() for _ in appended]

    return " ".join(new_append)


def calculate_time(time: int, unit: str) -> datetime:
    """
    計算時間差異，並回傳 datetime 物件。
    其中時間必須小於 365 天，單位必須為 'd', 'm'

    Args:
        time: 多少單位時間
        unit: 單位

    Returns:
        datetime: 計算後的時間

    Raises:
        ValueError: 單位不符合或時間超過 365 天
    """
    now_time: datetime = datetime.now(TIMEZONE)
    delta: timedelta = timedelta()

    if unit == "d":
        if time < 365:
            delta = timedelta(days=time)

    elif unit == "m":
        if time < 365 * 24 * 60:
            delta = timedelta(minutes=time)

    else:
        raise ValueError("單位必須是 'd' 或 'm' 且時間必須小於 365 天")

    calculated_time: datetime = now_time + delta

    if calculated_time - datetime.now(TIMEZONE) <= timedelta(seconds=58):
        raise ValueError("時間太短！")

    return calculated_time


async def graceful_calculate_time(
    msg: types.Message, time: str, unit: str
) -> datetime | None:
    try:
        return calculate_time(int(time), unit)

    except ValueError:
        await msg_auto_clean(
            await msg.reply_text(
                f"<b>錯誤：你輸入了一個無效的時間單位：{time}{unit}</b>\n"
                f"總時長必須小於 365 天\n"
                f"時間單位必須是 <code>d</code> 或 <code>m</code>"
            )
        )
        return


def get_until_time_message(msg: types.Message, until_date: datetime, size: int) -> str:
    message: str = (
        f"<b>直到：</b><code>{until_date.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
    )

    if size == 3:
        message += f"<b>原因：</b>{' '.join(msg.command[2:])}"

    return message


async def msg_auto_clean(msg: types.Message, time: int = 10):
    await asyncio.sleep(time)
    await msg.delete()
