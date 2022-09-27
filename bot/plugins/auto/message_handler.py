import logging

from pyrogram import Client, types
from pyrogram.enums import ChatType

from core.decorator import event_log
from core.log import main_logger, event_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(group=-1)
@event_log
def message_handler(cli: Client, msg: types.Message) -> None:
    if msg.chat.type != ChatType.SUPERGROUP:
        logger.warning(f"{msg.chat.type} is not SUPERGROUP, skipping...")
        return
