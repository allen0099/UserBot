import logging

from pyrogram import Client, Filters, Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("ping", prefixes=["$", "/"]))
def ping(cli: Client, msg: Message) -> None:
    msg.reply_text("pong")
