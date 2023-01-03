import logging

from pyrogram import Client, errors, filters, types
from pyrogram.enums import ChatType

from bot import Bot
from bot.functions import get_chat_link
from bot.methods.send_log_message import LogTopics
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.privilege import Privilege

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.group & ~filters.media_group, group=-99)
@event_log()
async def privilege_handler(cli: Bot, msg: types.Message) -> None:
    if msg.chat.type != ChatType.SUPERGROUP:
        return

    group: Privilege | None = Privilege.get(msg.chat.id)

    if not group:
        await cli.send_log_message(
            f"#privilege\n"
            f"Privilege not found!\n"
            f"Adding privilege for {get_chat_link(msg.chat)}",
            LogTopics.auto,
        )

        try:
            await Privilege.create_or_update(msg)

        except errors.UserNotParticipant:
            await cli.send_log_message(
                f"#privilege #error\n"
                f"User not in {get_chat_link(msg.chat)}, skipping...",
                LogTopics.auto,
            )
