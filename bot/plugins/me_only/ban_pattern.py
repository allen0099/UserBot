import logging
import re

from pyrogram import Client, filters, types
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
    if len(msg.command) != 2:
        await msg.edit("請輸入一個正規表達式")
        return

    pattern: str = msg.command[1]

    try:
        compiled: re.Pattern = re.compile(pattern)
    except re.error as e:
        await msg.edit(f"正規表達式錯誤：{e}")
        return

    members: list[types.ChatMember] = [
        user async for user in cli.get_chat_members(msg.chat.id)
    ]

    count: int = 0
    message: types.Message = await cli.send_message(
        msg.chat.id, f"找到了 {len(members)} 個使用者，正在進行檢查..."
    )

    for member in members:
        full_name: str = f"{member.user.first_name} {member.user.last_name}"
        logger.debug(f"Checking {member.user.id}")

        if compiled.match(member.user.first_name):
            count += 1
            logger.debug(f"{full_name} match pattern, remove from group!")
            await cli.ban_chat_member(msg.chat.id, member.user.id)

    logger.debug("Remove matched accounts finished!")
    await msg_auto_clean(
        await message.edit(f"在這個群組內踢了 <b>{count}</b> 個 <b><u>符合條件的帳號</u></b>！")
    )
