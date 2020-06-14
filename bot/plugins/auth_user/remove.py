import logging
import re
from typing import Union

from pyrogram import Client, Message, Filters
from pyrogram.api import types

from bot.functions import get_full_user
from bot.plugins import COMMAND_PREFIX
from bot.plugins.auth_user import USERNAME_RE
from models import Users

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(Filters.command("user_remove", prefixes=COMMAND_PREFIX) & Filters.me)
def user_remove(cli: Client, msg: Message) -> None:
    if len(msg.command) != 2:
        msg.reply_text("Usage:\n"
                       "<code>user_remove [UID, username, t.me link]</code>")
        return
    else:
        cmd: str = re.search(USERNAME_RE, msg.command[1])[0]

    full_user: Union[str, types.UserFull] = get_full_user(cli, cmd)

    if isinstance(full_user, types.UserFull):
        _user: types.User = full_user.user
        uid: int = int(repr(_user.id))
        if Users.remove(uid):
            string: str = f"Removed <code>{uid}</code> successfully"
        else:
            string: str = f"Not removed <code>{uid}</code>, because its not in list"
    else:
        string: str = full_user
    msg.reply_text(string)
