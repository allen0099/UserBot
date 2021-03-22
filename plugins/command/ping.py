import logging

from pyrogram import Client, filters
from pyrogram.types import Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("ping", prefixes="$") & filters.me & ~ filters.forwarded)
def ping(_: Client, msg: Message) -> None:
    msg.reply_text("pong")
