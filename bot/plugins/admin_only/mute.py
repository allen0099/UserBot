import logging
from datetime import datetime, timedelta

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMemberStatus

from bot import Bot
from bot.filters import admin_required
from bot.functions import get_mute_permission, msg_auto_clean
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
                await cli.ban_chat_member(msg.chat.id, target.id)
                permission: types.ChatPermissions = get_mute_permission()

                try:
                    until_time: datetime = get_until(msg.command[1].lower())
                except (ValueError, IndexError):
                    await msg.reply_text("你的時間錯誤！")
                    return

                await cli.restrict_chat_member(
                    msg.chat.id, target.id, permission, until_time
                )

                await msg_auto_clean(
                    await msg.reply_text(f"已給 {target.mention} 上了口球，直到 {until_time}")
                )
                return

            await msg_auto_clean(await msg.reply_text(f"<b>錯誤：你無法對管理員下手！</b>"))

        elif isinstance(target, types.Chat):
            await msg_auto_clean(
                await msg.reply_text(f"<b>錯誤：你正在試圖給予頻道口球，但這不合理\n請給予一個使用者口球。</b>")
            )
        return

    await msg_auto_clean(await msg.reply_text("<b>錯誤：你必須回覆一個使用者以給予口球。</b>"))


def get_until(until: str) -> datetime:
    _: datetime = datetime.now()
    if until.endswith("d"):
        days: int = int(until.split("d")[0])
        if days < 365:
            _ += timedelta(days=days)

    if until.endswith("m"):
        minutes: int = int(until.split("m")[0])
        if minutes < 60 * 24 * 365:
            _ += timedelta(minutes=minutes)

    if _ - datetime.now() <= timedelta(seconds=58):
        raise ValueError("時間太短！")
    return _
