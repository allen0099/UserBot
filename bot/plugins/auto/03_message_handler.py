import logging

from pyrogram import Client, filters, types
from pyrogram.enums import ChatType

from bot import Bot
from bot.functions import get_chat_link
from bot.methods.send_log_message import LogTopics
from bot.validation import UserValidator
from core.decorator import event_log
from core.log import event_logger, main_logger
from database.models.privilege import Privilege

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.group & ~filters.media_group, group=-98)
@event_log()
async def message_handler(cli: Bot, msg: types.Message) -> None:
    if msg.chat.type != ChatType.SUPERGROUP:
        return

    if msg.chat.id in Privilege.admin_group_list() and msg.from_user is not None:
        uv: UserValidator = UserValidator(msg.from_user)
        uv.validate()

        if uv.errors:
            await cli.send_log_message(
                f"#banned "
                f"#{' #'.join(uv.errors)}\n"
                f"User: {msg.from_user.mention}\n"
                f"User ID: <code>{msg.from_user.id}</code>\n"
                f"Group: {get_chat_link(msg.chat)}\n"
                f"Message Link: {msg.link}",
                LogTopics.banned,
            )
            # TODO: act something ban user (implement in next version)
