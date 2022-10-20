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
    filters.command("killda", prefixes=COMMAND_PREFIXES)
    & admin_required
    & filters.group
    & ~filters.forwarded
)
@event_log()
async def kill_da(cli: Bot, msg: types.Message):
    await msg.delete()

    members: list[types.ChatMember] = [
        user async for user in cli.get_chat_members(msg.chat.id)
    ]

    count: int = 0
    message: types.Message = await cli.send_message(
        msg.chat.id, f"找到了 {len(members)} 個使用者，正在進行檢查..."
    )

    for member in members:
        log.debug(f"Checking {member.user.id}")

        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            continue

        if member.user.is_deleted:
            count += 1
            log.debug(f"{member.user.id} is deleted, remove from group!")
            await cli.kick_chat_member(msg.chat.id, member.user.id)

    log.debug("Remove deleted accounts finished!")
    await msg_auto_clean(
        await message.edit(f"在這個群組內踢了 <b>{count}</b> 個 <b><u>已刪除的帳號</u></b>！")
    )
