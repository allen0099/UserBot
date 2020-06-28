import logging
from typing import Union, Generator

import pyrogram
from pyrogram import Client
from pyrogram.api import types, functions
from pyrogram.errors import PeerIdInvalid, UsernameInvalid

from models.chats import WithPermission, WithoutPermission, NoPermission

log: logging.Logger = logging.getLogger(__name__)


def get_full_user(cli: Client, cmd: str) -> Union[str, types.UserFull]:
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


def restart(cli: Client) -> None:
    from threading import Thread
    Thread(target=cli.restart).start()


def recheck_permission_chats(cli: Client) -> None:
    r: Generator["pyrogram.Dialog"] = cli.iter_dialogs()

    for _ in r:
        if _.chat.type == "supergroup" and \
                not WithPermission.is_saved(_.chat.id) and \
                not WithoutPermission.is_saved(_.chat.id) and \
                not NoPermission.is_saved(_.chat.id):
            permission: pyrogram.ChatMember = cli.get_chat_member(_.chat.id, cli.get_me().id)

            log.debug(f"{_.chat.id} {permission.status}")

            _sort_chats(permission, _.chat.id)


def _sort_chats(permission: pyrogram.ChatMember, cid: int) -> None:
    if permission.status == "creator":
        WithPermission.add(cid)

    if permission.status == "administrator" and \
            permission.can_delete_messages is True and \
            permission.can_restrict_members is True:
        WithPermission.add(cid)
    else:
        NoPermission.add(cid)

    if permission.status == "member":
        WithoutPermission.add(cid)

    if permission.status == "restricted":
        NoPermission.add(cid)
