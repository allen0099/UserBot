import logging
from typing import List

import pyrogram
from pyrogram import Client, Message, Filters

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("admin", "@") & Filters.group & Filters.me)
def mention_admins(cli: Client, msg: Message) -> None:
    cli.delete_messages(msg.chat.id, [msg.message_id])

    admins: List[pyrogram.ChatMember] = \
        cli.get_chat_members(msg.chat.id,
                             filter="administrators")

    string: str = "admins"
    for admin in admins:
        string += f"<a href='tg://user?id={admin.user.id}'>" + "\u2060" + "</a>"
    cli.send_message(msg.chat.id,
                     string,
                     parse_mode="HTML",
                     disable_notification=False)
