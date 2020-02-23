import logging

from pyrogram import Client, Filters, Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("getchat", prefixes="$"))
def get_chat(cli: Client, msg: Message) -> None:
    msg.reply_text(msg.chat.id)
