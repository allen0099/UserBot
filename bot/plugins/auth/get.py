import logging

from pyrogram import Client, Message, Filters

from bot.plugins import COMMAND_PREFIX
from models import Users

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("user_get", prefixes=COMMAND_PREFIX) & Filters.me)
def user_get(cli: Client, msg: Message) -> None:
    msg.reply_text(f"Users: <code>{Users.get()}</code>")
