import logging

from pyrogram import Client, Filters, Message

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("getme", prefixes="$"))
def get_me(cli: Client, msg: Message) -> None:
    msg.reply_text(msg.from_user.id)
