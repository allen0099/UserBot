import logging

from pyrogram import Client, filters
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember, Message

from bot.custom_filters import admin_required
from bot.functions import get_members

log: logging.Logger = logging.getLogger(__name__)

__USAGE__: str = "Usage: <code>bail {kick|restrict}</code>"
KICKED: list[str] = ["kick", "kicked"]
RESTRICTED: list[str] = ["restrict", "restricted"]


@Client.on_message(filters.command("bail", prefixes="!") & filters.me & admin_required)
async def bail(cli: Client, msg: Message):
    if len(msg.command) == 2:
        log.debug(f"Bailing out {msg.command[1].lower()} users...")
        if msg.command[1].lower() in KICKED:
            members: list[ChatMember] = await get_members(cli, msg.chat.id, choose=Filters.KICKED)
        elif msg.command[1].lower() in RESTRICTED:
            members: list[ChatMember] = await get_members(cli, msg.chat.id, choose=Filters.RESTRICTED)
        else:
            await msg.reply_text(__USAGE__)
            return
    else:
        await msg.reply_text(__USAGE__)
        return

    count: int = 0

    log.debug(f"{len(members)} found!")
    message: Message = await cli.send_message(msg.chat.id, f"Cleaning the list...({count}/{len(members)})")

    for _ in members:
        count += 1

        log.debug(f"Bailing out uid: {_.user.id}")
        log.debug(f"Progress: {count}/{len(members)}")

        if count % 50 == 1:
            await message.edit(f"Cleaning the list...({count}/{len(members)})")
        await cli.unban_chat_member(msg.chat.id, _.user.id)

    log.debug("Bail finished!")
    await message.edit(f"{count} <b><u>{msg.command[1]} user(s)</u></b> released!")
