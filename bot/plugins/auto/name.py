import html
import logging
from typing import List

from pyrogram import Client, Message, Filters

from bot.functions import CheckRules
from bot.plugins import LOG_CHANNEL
from models.chats import CreatorChats, AdminChats
from models.rules.NameRules import NameRules

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.chat(CreatorChats.list_all() + AdminChats.list_all()) & Filters.new_chat_members)
def name_check(cli: Client, msg: Message) -> None:
    full_name: str = f"{msg.from_user.first_name} {msg.from_user.last_name}"

    rules: List[str] = [r.rule for r in NameRules.get_all()]
    reply: str = f"User: <a href='tg://user?id={msg.from_user.id}'>{html.escape(full_name)}</a>" \
                 f" [<code>{msg.from_user.id}</code>]\n" \
                 f"Group: {html.escape(msg.chat.title)}" \
                 f" [<code>{msg.chat.id}</code>]\n"

    log.debug(f"Full Name: {full_name}")

    check: CheckRules = CheckRules(full_name, rules)
    if check:
        reply += check
        # ban later

    cli.send_message(LOG_CHANNEL, reply)
