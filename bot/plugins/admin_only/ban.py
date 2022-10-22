import logging
import re
from datetime import datetime
from html import escape
from re import Pattern

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMemberStatus

from bot import Bot
from bot.filters import admin_required
from bot.functions import (
    get_until_time_message,
    graceful_calculate_time,
    msg_auto_clean,
)
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger

log: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("ban", prefixes=COMMAND_PREFIXES)
    & admin_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def ban(cli: Bot, msg: types.Message) -> None:
    await msg.delete()

    if msg.reply_to_message:
        target: types.Chat | types.User = (
            msg.reply_to_message.from_user or msg.reply_to_message.sender_chat
        )  # From channel or user

        if isinstance(target, types.User):
            chat_user: types.ChatMember = await cli.get_chat_member(
                msg.chat.id, target.id
            )

            if chat_user.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
            ]:
                await _ban_helper(cli, msg, target)
                return

            await msg_auto_clean(await msg.reply_text(f"<b>錯誤：你無法對管理員下手！</b>"))

        elif isinstance(target, types.Chat):
            channel: types.Chat = await cli.get_chat(target.id)

            if (
                channel.linked_chat
                and channel.linked_chat.id == msg.chat.id
                or channel.id == msg.chat.id
            ):
                await msg_auto_clean(await msg.reply_text(f"<b>錯誤：這是本群的連結頻道！</b>"))
                return

            await _ban_helper(cli, msg, target)
        return

    await msg_auto_clean(await msg.reply_text("<b>資訊錯誤：訊息已被刪除或是未回覆訊息導致無法取得資訊。</b>"))


async def _ban_helper(cli: Bot, msg: types.Message, target: types.Chat | types.User):
    message: str = f""
    time_re: Pattern = re.compile(r"(^\d+)(d$|m$)")

    if isinstance(target, types.User):
        message += f"已封鎖使用者 {target.mention}\n"

    elif isinstance(target, types.Chat):
        message += f"已封鎖頻道 <code>{escape(target.title)}({target.id})</code>\n"

    else:
        raise TypeError("目標必須是 types.User 或 types.Chat")

    match len(msg.command):
        case 1:
            message += "<b>直到：</b><code>永久</code>\n"
            await cli.ban_chat_member(msg.chat.id, target.id)

        case 2 | 3 as size:
            test: list[tuple[str, str]] | None = re.findall(time_re, msg.command[1])

            if test:
                time, unit = test[0]

                until_date: datetime | None = await graceful_calculate_time(
                    msg, time, unit
                )

                if not until_date:
                    return

                message += get_until_time_message(msg, until_date, size)
                await cli.ban_chat_member(msg.chat.id, target.id, until_date)

            else:
                message += (
                    f"<b>直到：</b><code>永久</code>\n"
                    f"<b>原因：</b>{' '.join(msg.command[1:])}"
                )
                await cli.ban_chat_member(msg.chat.id, target.id)

        case _:
            message += (
                f"<b>直到：</b><code>永久</code>\n<b>原因：</b>{' '.join(msg.command[1:])}"
            )
            await cli.ban_chat_member(msg.chat.id, target.id)

    await msg.reply_text(message)
