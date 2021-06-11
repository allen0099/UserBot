import logging

from pyrogram import Client, filters
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember, Message

from bot.filters import CustomFilters
from bot.functions import CustomFunctions

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("killda", prefixes="!") & CustomFilters.admin_required)
async def kill_da(cli: Client, msg: Message):
    members: list[ChatMember] = await CustomFunctions.get_members(cli, msg.chat.id, choose=Filters.ALL)

    count: int = 0
    message: Message = await cli.send_message(msg.chat.id, f"{len(members)} users found!")

    for _ in members:
        log.debug(f"Checking {_.user.id}")
        if _.user.is_deleted:
            count += 1
            log.debug(f"{_.user.id} is deleted, remove from group!")
            await cli.kick_chat_member(msg.chat.id, _.user.id)
            await cli.unban_chat_member(msg.chat.id, _.user.id)

    log.debug("Remove deleted accounts finished!")
    await message.edit(f"Removed <b>{count}</b> <b><u>deleted account(s)</u></b> in this group!")
