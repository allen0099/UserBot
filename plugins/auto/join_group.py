import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatType, MessageServiceType
from pyrogram.types import Message

from database.gbanlog import GBanLog
from database.privilege import Privilege
from database.users import User

log: logging.Logger = logging.getLogger(__name__)


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

    blacklist: list[int] = User.get_blacklist()
    for user in msg.new_chat_members:
        if user.id in blacklist:
            log.debug(f"User {user.id} is in blacklist, banning...")
            GBanLog.create(user.id, msg.chat.id)
            await cli.ban_chat_member(msg.chat.id, user.id)
