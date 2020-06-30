import logging
import re

from pyrogram import Client, Message, Filters

from bot.plugins import COMMAND_PREFIX
from bot.plugins.auth import CMD_RE
from models.rules import NameRules

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("name_get", prefixes=COMMAND_PREFIX) & Filters.me)
def name_get(cli: Client, msg: Message) -> None:
    string: str = f"Names: <code>\n"
    for rule in NameRules.get_rules():
        string += f"{rule}\n"
        string += f"========\n"
    string += f"</code>"
    msg.reply_text(string)


@Client.on_message(Filters.command("name_add", prefixes=COMMAND_PREFIX) & Filters.me)
def name_add(cli: Client, msg: Message) -> None:
    cmd: str = re.search(CMD_RE, msg.text)[0]
    if NameRules.add(cmd):
        string: str = f"Added <code>{cmd}</code> successfully"
    else:
        string: str = f"Not add <code>{cmd}</code>, because its already in list"
    msg.reply_text(string)


@Client.on_message(Filters.command("name_remove", prefixes=COMMAND_PREFIX) & Filters.me)
def name_remove(cli: Client, msg: Message) -> None:
    _id: str = re.search(CMD_RE, msg.text)[0]
    if NameRules.remove(_id):
        string: str = f"Removed <code>{_id}</code> successfully"
    else:
        string: str = f"Not removed <code>{_id}</code>, because its not in list"
    msg.reply_text(string)


@Client.on_message(Filters.command("name_search", prefixes=COMMAND_PREFIX) & Filters.me)
def name_search(cli: Client, msg: Message) -> None:
    rule: str = re.search(CMD_RE, msg.text)[0]
    msg.reply_text(f"ID: <code>{NameRules.get_id(rule)}</code>")
