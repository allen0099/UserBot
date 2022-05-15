import html
import logging
import os

from pyrogram import Client, filters
from pyrogram.enums import ChatType, MessageServiceType
from pyrogram.types import Message

from database.gbanlog import GBanLog
from database.privilege import Privilege
from plugins.utils import is_black_listed_user

log: logging.Logger = logging.getLogger(__name__)
LOG_CHANNEL: str = os.getenv("LOG_CHANNEL")

@Client.on_message(filters.service, group=-1)
async def join_group(cli: Client, msg: Message) -> None:
    """
    Ban user if user is in blacklist when user try to join the group.
    """
    groups = Privilege.admin_groups()
    if msg.chat.id not in groups:
        return

    if msg.chat.type != ChatType.SUPERGROUP:
        return

    if msg.service != MessageServiceType.NEW_CHAT_MEMBERS:
        return

    for user in msg.new_chat_members:
        log.debug(f"User {user.id} joined {msg.chat.title}")
        if is_black_listed_user(user):
            log.debug(f"User {user.id} is in blacklist, banning...")
            await msg.delete()
            GBanLog.create(user.id, msg.chat.id)
            await cli.ban_chat_member(msg.chat.id, user.id)

            await cli.send_message(
                LOG_CHANNEL,
                f"#userbot #ban #blacklist\n"
                f"User: {user.id} is in blacklist\n"
                f"Joined: <code>{html.escape(msg.chat.title)}</code>(<code>{msg.chat.id}</code>)\n"
            )
