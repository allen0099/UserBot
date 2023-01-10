import logging

from pyrogram import Client, filters, types
from pyrogram.types import Message

from bot import Bot
from bot.enums import LogTopics, PermissionLevel
from bot.functions import get_target, msg_auto_clean
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.users import Users

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("add_executor", prefixes=COMMAND_PREFIXES)
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def add_executor(cli: Bot, msg: Message) -> None:
    await msg.delete()

    user: types.User | types.Chat = await get_target(cli, msg)

    if not isinstance(user, types.User):
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"操作失敗，必須為使用者",
            )
        )
        return

    db_user: Users = Users.get(user.id)

    if db_user.permission_level == PermissionLevel.EXECUTOR:
        await msg_auto_clean(
            await cli.send_message(
                msg.chat.id,
                f"操作失敗，使用者已經是執行者",
            )
        )
        return

    db_user.level = PermissionLevel.EXECUTOR
    db_user.locked = True
    db_user.add()

    await msg_auto_clean(
        await cli.send_log_message(
            f"✅ #add_executor\n新增執行者：{user.mention} (<code>{user.id}</code>)\n",
            LogTopics.action,
        )
    )
