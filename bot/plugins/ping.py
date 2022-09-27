import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from core.decorator import event_log
from core.log import main_logger

log: logging.Logger = main_logger(__name__)


@Client.on_message(filters.command("ping") & ~filters.forwarded)
@event_log
async def ping(_: Client, msg: Message) -> None:
    """
    Return pong.

    Args:
        _:
        msg:

    Returns:
        None
    """
    await msg.reply_text("pong!")
