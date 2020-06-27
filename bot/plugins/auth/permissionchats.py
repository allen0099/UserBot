from pyrogram import Client, Filters, Message

from bot.plugins import COMMAND_PREFIX
from models import PermissionChats


@Client.on_message(Filters.command("permission_list", prefixes=COMMAND_PREFIX) & Filters.me)
def permission_list(cli: Client, msg: Message) -> None:
    msg.reply_text(f"Chats: <code>{PermissionChats.get()}</code>")
