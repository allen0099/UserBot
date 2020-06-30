import html
import logging
import re
from typing import List

from pyrogram import Client, Message, Filters

from bot.plugins import COMMAND_PREFIX
from bot.plugins.auth import CMD_RE
from models.rules import NameRules

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("name_add", prefixes=COMMAND_PREFIX) & Filters.me)
def name_add(cli: Client, msg: Message) -> None:
    cmd: str = re.search(CMD_RE, msg.text)[0]
    if NameRules.add(cmd):
        reply: str = f"Added <code>{html.escape(cmd)}</code> successfully"
    else:
        reply: str = f"Not add <code>{html.escape(cmd)}</code>, because its already in list"
    msg.reply_text(reply)


@Client.on_message(Filters.command("name_remove", prefixes=COMMAND_PREFIX) & Filters.me)
def name_remove(cli: Client, msg: Message) -> None:
    _id: str = re.search(CMD_RE, msg.text)[0]
    if NameRules.remove(_id):
        reply: str = f"Removed <code>{_id}</code> successfully"
    else:
        reply: str = f"Not removed <code>{_id}</code>, because its not in list"
    msg.reply_text(reply)


@Client.on_message(Filters.command("name_get", prefixes=COMMAND_PREFIX) & Filters.me)
def name_get(cli: Client, msg: Message) -> None:
    reply: str = f"<code> ID | RULE</code>\n" \
                 f"<code>==========</code>\n"
    for rule in NameRules.get_all():
        reply += f"<code>{rule.id:^4}| {html.escape(rule.rule)}</code>\n"
    msg.reply_text(reply)


@Client.on_message(Filters.command("name_edit", prefixes=COMMAND_PREFIX) & Filters.me)
def name_edit(cli: Client, msg: Message) -> None:
    cmd: List[str] = re.search(CMD_RE, msg.text)[0].split(" ", 1)
    _id: str = cmd[0]
    new_rule: str = cmd[1]

    if _id.isdigit():
        _id: int = int(_id)

        reply: str = f"Edit <code>{_id}</code> " \
                     f"from <code>{html.escape(NameRules.find_by_id(_id).rule)}</code> " \
                     f"to <code>{html.escape(new_rule)}</code>"

        if NameRules.edit(_id, new_rule):
            msg.reply_text(reply)
    else:
        msg.reply_text(f"ID <code>{_id}</code> not found")
