import logging

from pyrogram import Client, Message, Filters

from plugins.auth_ban import user

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("add_auth", prefixes="$") & Filters.me)
def add_auth(cli: Client, msg: Message) -> None:
    uid: int = int(msg.command[1])
    user.add_auth(uid)
    msg.reply_text(f"Add {uid} successfully")
