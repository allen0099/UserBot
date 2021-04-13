import logging

from pyrogram import Client, filters
from pyrogram.methods.chats.get_chat_members import Filters
from pyrogram.types import ChatMember, Message

from main import user_bot

log: logging.Logger = logging.getLogger(__name__)

__USAGE__: str = "Usage: <code>bail {kick|restrict}</code>"
KICKED: list[str] = ["kick", "kicked"]
RESTRICTED: list[str] = ["restrict", "restricted"]


@Client.on_message(filters.command("bail", prefixes="!") & filters.me)
async def bail(cli: Client, msg: Message):
    me: ChatMember = await cli.get_chat_member(msg.chat.id, user_bot.me.id)
    if not me.can_restrict_members or not me.can_delete_messages:
        await msg.reply_text("<b>Permission denied</b>")
        return

    if len(msg.command) == 2:
        if msg.command[1].lower() in KICKED:
            members: list[ChatMember] = await cli.get_chat_members(msg.chat.id, filter=Filters.KICKED)
        elif msg.command[1].lower() in RESTRICTED:
            members: list[ChatMember] = await cli.get_chat_members(msg.chat.id, filter=Filters.RESTRICTED)
        else:
            await msg.reply_text(__USAGE__)
            return
    else:
        await msg.reply_text(__USAGE__)
        return

    for _ in members:
        await cli.unban_chat_member(msg.chat.id, _.user.id)

    await msg.reply_text(f"Released <b><u>{msg.command[1]}</u></b> users finished!")
