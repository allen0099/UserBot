from typing import Generator

import pyrogram
from pyrogram import Client

from _bot_old.functions import log
from _models_old.chats import CreatorChats, AdminChats, MemberChats, RestrictedChats


def iter_supergroups(cli: Client) -> None:
    r: Generator["pyrogram.Dialog"] = cli.iter_dialogs()

    for _ in r:
        if _.chat.type == "supergroup" and \
                not CreatorChats.is_exist(_.chat.id) and \
                not AdminChats.is_exist(_.chat.id) and \
                not MemberChats.is_exist(_.chat.id) and \
                not RestrictedChats.is_exist(_.chat.id):
            permission: pyrogram.ChatMember = cli.get_chat_member(_.chat.id, cli.get_me().id)

            log.debug(f"{_.chat.id} {permission.status}")

            _filter(permission, _.chat.id)


def _filter(permission: pyrogram.ChatMember, cid: int) -> None:
    if permission.status == "creator":
        CreatorChats.add(cid)

    if permission.status == "administrator" and \
            permission.can_delete_messages is True and \
            permission.can_restrict_members is True:
        AdminChats.add(cid)
    else:
        RestrictedChats.add(cid)

    if permission.status == "member":
        MemberChats.add(cid)

    if permission.status == "restricted":
        RestrictedChats.add(cid)
