import logging

from pyrogram import Client, Filters, Message

from bot.plugins import COMMAND_PREFIX

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("ping", prefixes=COMMAND_PREFIX) & Filters.me)
def ping(cli: Client, msg: Message) -> None:
    msg.reply_text("pong")
