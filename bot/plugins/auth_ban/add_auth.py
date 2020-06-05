import logging
import re
from typing import Union, Pattern

from pyrogram import Client, Message, Filters
from pyrogram.api import types, functions
from pyrogram.errors import PeerIdInvalid, UsernameInvalid

from bot.plugins.auth_ban import user

log: logging.Logger = logging.getLogger(__name__)
USERNAME_RE: Pattern[str] = re.compile(r"(?<=t\.me/)\w{5,}$|(?<=@)\w{5,}$|\w{5,}$|^[+-]?\d+$|me$|self$")


@Client.on_message(Filters.command("add_auth", prefixes="$") & Filters.me)
def add_auth(cli: Client, msg: Message) -> None:
    cmd: str = re.search(USERNAME_RE, msg.command[1])[0]

    full_user: Union[str, types.UserFull] = _get_user_full(cli, cmd)

    if isinstance(full_user, types.UserFull):
        _user: types.User = full_user.user
        uid: int = int(repr(_user.id))
        user.add_auth(uid)
        string: str = f"Added <code>{uid}</code> successfully"
    else:
        string: str = full_user
    msg.reply_text(string)


@Client.on_message(Filters.command("remove_auth", prefixes="$") & Filters.me)
def remove_auth(cli: Client, msg: Message) -> None:
    cmd: str = re.search(USERNAME_RE, msg.command[1])[0]

    full_user: Union[str, types.UserFull] = _get_user_full(cli, cmd)

    if isinstance(full_user, types.UserFull):
        _user: types.User = full_user.user
        uid: int = int(repr(_user.id))
        user.remove_auth(uid)
        string: str = f"Removed <code>{uid}</code> successfully"
    else:
        string: str = full_user
    msg.reply_text(string)


@Client.on_message(Filters.command("list_auth", prefixes="$") & Filters.me)
def list_auth(cli: Client, msg: Message) -> None:
    msg.reply_text(f"Users: <code>{user.get_auth()}</code>")


def _get_user_full(cli: Client, cmd: str) -> Union[str, types.UserFull]:
    try:
        _user_full: types.UserFull = cli.send(
            functions.users.GetFullUser(
                id=cli.resolve_peer(cmd)
            )
        )
    except PeerIdInvalid as e:
        return str(e.CODE) + " " + e.ID
    except UsernameInvalid as e:
        return str(e.CODE) + " " + e.ID
    else:
        return _user_full
