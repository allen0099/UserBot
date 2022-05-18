import asyncio
import logging

from pyrogram import Client, enums, filters, types
from pyrogram.types import Message

from database.privilege import Privilege
from plugins.utils import is_white_list_user

log: logging.Logger = logging.getLogger(__name__)


async def is_allowed_user(msg: Message) -> bool:
    if msg.sender_chat:
        return False

    if msg.from_user.is_self:
        return True

    if is_white_list_user(msg.from_user):
        return True

    admin_list: list[types.ChatMember] = []
    async for admin in msg.chat.get_members(filter=enums.ChatMembersFilter.ADMINISTRATORS):
        admin_list.append(admin)

    if msg.from_user.id in [admin.user.id for admin in admin_list]:
        return True

    if msg.chat.type != enums.ChatType.SUPERGROUP:
        return False

    if msg.from_user.is_bot:
        return False

    return False


@Client.on_message(filters.command("update", prefixes="!"))
async def update(cli: Client, msg: Message) -> None:
    """
    Update the bot.

    Usage: ``!update``
    """
    if not await is_allowed_user(msg):
        return

    # update group privileges
    privilege: Privilege = Privilege.get(msg.chat.id)

    if privilege:
        await privilege.update(msg)
        m: types.Message = await cli.send_message(msg.chat.id, "Permission in this group has been updated.")
        if msg.from_user.is_self:
            await msg.delete()
        await asyncio.sleep(5)
        await m.delete()
