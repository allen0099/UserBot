import logging
import random

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("random", prefixes="$") & filters.me)
def roll(_: Client, msg: Message) -> None:
    if len(msg.command) == 1:
        msg.reply(str(random.randint(1, 6)))
    elif len(msg.command) == 2 and msg.command[1].isdigit():
        msg.reply(str(random.randint(1, int(msg.command[1]))))
    else:
        msg.reply(random.choice(msg.command[1::]))
