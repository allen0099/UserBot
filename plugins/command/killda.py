import logging

from pyrogram import Client, filters
from pyrogram.types import ChatMember, Message

from main import user_bot

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("killda", prefixes="!") & filters.me)
async def kill_da(cli: Client, msg: Message):
    me: ChatMember = await cli.get_chat_member(msg.chat.id, user_bot.me.id)
    if not me.can_restrict_members or not me.can_delete_messages:
        await msg.reply_text("<b>Permission denied</b>")
        return

    members: list[ChatMember] = await cli.get_chat_members(msg.chat.id)

    for _ in members:
        if _.user.is_deleted:
            await cli.kick_chat_member(msg.chat.id, _.user.id)
            await cli.unban_chat_member(msg.chat.id, _.user.id)

    await msg.reply_text("Cleared deleted accounts in this group!")
