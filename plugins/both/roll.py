import logging
import random

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("random", prefixes="!") & filters.me & ~ filters.forwarded)
async def roll(_: Client, msg: Message) -> None:
    """
    Rolls a die with the specified number of sides, default is a six-sided die.

    Usage: ``!random <number>`` or ``!random <choices>``
    """
    if len(msg.command) == 1:
        await msg.reply(str(random.randint(1, 6)))
    elif len(msg.command) == 2 and msg.command[1].isdigit():
        await msg.reply(str(random.randint(1, int(msg.command[1]))))
    else:
        await msg.reply(random.choice(msg.command[1::]))
