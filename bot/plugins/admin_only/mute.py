import logging
import re
from datetime import datetime
from re import Pattern

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMemberStatus

from bot import Bot
from bot.filters import admin_required
from bot.functions import (
    get_mute_permission,
    get_until_time_message,
    graceful_calculate_time,
    msg_auto_clean,
)
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger

log: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("mute", prefixes=COMMAND_PREFIXES)
    & admin_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def mute(cli: Bot, msg: types.Message):
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
                permission: types.ChatPermissions = get_mute_permission()
                await _mute_helper(cli, msg, target, permission)
                return

            await msg_auto_clean(await msg.reply_text(f"<b>錯誤：你無法對管理員下手！</b>"))

        elif isinstance(target, types.Chat):
            await msg_auto_clean(
                await msg.reply_text(f"<b>錯誤：你正在試圖給予頻道口球，但這不合理\n請給予一個使用者口球。</b>")
            )
        return

    await msg_auto_clean(await msg.reply_text("<b>錯誤：你必須回覆一個使用者以給予口球。</b>"))


async def _mute_helper(
    cli: Bot, msg: types.Message, target: types.User, permission: types.ChatPermissions
):
    message: str = f""
    time_re: Pattern = re.compile(r"(^\d+)(d$|m$)")

    if isinstance(target, types.User):
        message += f"已給予 {target.mention} 上了口球\n"

    else:
        raise TypeError("目標必須是 types.User")

    match len(msg.command):
        case 1:
            message += "<b>直到：</b><code>永久</code>\n"
            await cli.restrict_chat_member(msg.chat.id, target.id, permission)

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
                await cli.restrict_chat_member(
                    msg.chat.id, target.id, permission, until_date
                )

            else:
                message += (
                    f"<b>直到：</b><code>永久</code>\n"
                    f"<b>原因：</b>{' '.join(msg.command[1:])}"
                )
                await cli.restrict_chat_member(msg.chat.id, target.id, permission)

        case _:
            message += (
                f"<b>直到：</b><code>永久</code>\n<b>原因：</b>{' '.join(msg.command[1:])}"
            )
            await cli.restrict_chat_member(msg.chat.id, target.id, permission)

    await msg.reply_text(message)
