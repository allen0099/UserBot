import logging
import random

from pyrogram import Client, filters
from pyrogram.types import Message

from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("roll", prefixes=COMMAND_PREFIXES) & filters.me & ~filters.forwarded
)
@event_log()
async def roll(_: Client, msg: Message) -> None:
    if len(msg.command) == 1:
        await msg.reply(f"{random.randint(1, 6)}")

    elif len(msg.command) == 2 and msg.command[1].isdigit():
        await msg.reply(f"{random.randint(1, int(msg.command[1]))}")

    else:
        await msg.reply(random.choice(msg.command[1::]))
