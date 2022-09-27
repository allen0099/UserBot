import logging

from pyrogram import Client, filters
from pyrogram.enums import MessageServiceType, ChatType
from pyrogram.types import Message

from core.decorator import event_log
from core.log import main_logger, event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(filters.service, group=-100)
@event_log
async def service_handler(cli: Client, msg: Message) -> None:
    """
    Ban user if user is in blacklist when user try to join the group.
    """
    if msg.chat.type != ChatType.SUPERGROUP:
        logger.warning(f"{msg.chat.type} is not SUPERGROUP, skipping...")
        return

    match msg.service:
        case MessageServiceType.NEW_CHAT_MEMBERS:
            if cli.me in msg.new_chat_members:
                logger.info(f"I am invited to {repr(msg.chat)}, do permission check...")

                await cli.send_message(msg.chat.id, "Hi, this is a test bot.")
                return

            for user in msg.new_chat_members:
                # Known issue: user approved by admin will not get any service message,
                # instead, bot will get a normal message which only contain message id, user, chat, and date.
                logger.debug(f"User {repr(user)} joined {repr(msg.chat)}")

        case MessageServiceType.LEFT_CHAT_MEMBERS if msg.left_chat_member.is_self:
            logger.info(
                f"Admin {repr(msg.from_user)} kicked me from {repr(msg.chat)}. Hope to see them again!"
            )
            return

        case _:
            logger.debug(f"{msg.service} is not handled, skipping...")
            return
