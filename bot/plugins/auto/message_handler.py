import logging

from pyrogram import Client, types
from pyrogram.enums import ChatType

from bot import Bot
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(group=-100)
@event_log()
def message_handler(_: Bot, msg: types.Message) -> None:
    if msg.chat.type != ChatType.SUPERGROUP:
        logger.warning(f"{msg.chat.type} is not SUPERGROUP, skipping...")
