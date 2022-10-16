import logging

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMemberStatus

from bot import Bot
from bot.filters import admin_required
from bot.functions import msg_auto_clean
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
                await cli.ban_chat_member(msg.chat.id, target.id)
                await msg_auto_clean(await msg.reply_text(f"已封鎖使用者 {target.mention}"))
                return

            await msg_auto_clean(await msg.reply_text(f"<b>錯誤：你無法對管理員下手！</b>"))

        elif isinstance(target, types.Chat):
            channel = await cli.get_chat(target.id)

            if (
                channel.linked_chat
                and channel.linked_chat.id == msg.chat.id
                or channel.id == msg.chat.id
            ):
                await msg_auto_clean(await msg.reply_text(f"<b>錯誤：這是本群的連結頻道！</b>"))
                return

            await cli.ban_chat_member(msg.chat.id, target.id)
            await msg_auto_clean(await msg.reply_text(f"已封鎖 <code>{target.id}</code>"))
        return

    await msg_auto_clean(await msg.reply_text("<b>錯誤：回覆群組中的訊息來封鎖使用者。</b>"))
