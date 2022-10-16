import logging
import re

from pyrogram import Client, filters, types
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from bot import Bot
from bot.functions import msg_auto_clean
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("pattern", prefixes=COMMAND_PREFIXES)
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def pattern(cli: Bot, msg: Message) -> None:
    await msg.delete()

    if len(msg.command) != 3:
        await msg_auto_clean(
            await msg.reply_text(
                "請輸入正確的指令！\n格式為：<code>/pattern [group_id] [pattern]</code>"
            )
        )
        return

    group_id: str = msg.command[1]
    pattern: str = msg.command[2]

    check_self: types.ChatMember = await cli.get_chat_member(group_id, cli.me.id)

    if (
        check_self.status
        not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
        or check_self.privileges.can_restrict_members is False
    ):
        await msg_auto_clean(await msg.reply_text("我不是管理員！"))
        return

    try:
        compiled: re.Pattern = re.compile(pattern)

    except re.error as e:
        await msg.edit(f"正規表達式錯誤：{e}")
        return

    members: list[types.ChatMember] = [
        user async for user in cli.get_chat_members(group_id)
    ]

    count: int = 0
    message: types.Message = await cli.send_message(
        group_id, f"找到了 {len(members)} 個使用者，正在進行檢查..."
    )

    for member in members:
        full_name: str = f"{member.user.first_name} {member.user.last_name}"
        logger.debug(f"Checking {member.user.id}")

        if compiled.match(full_name):
            count += 1
            logger.debug(f"{full_name} match pattern, remove from group!")
            await cli.ban_chat_member(group_id, member.user.id)

    logger.debug("Remove matched accounts finished!")
    await msg_auto_clean(
        await message.edit(f"在這個群組內踢了 <b>{count}</b> 個 <b><u>符合條件的帳號</u></b>！")
    )
