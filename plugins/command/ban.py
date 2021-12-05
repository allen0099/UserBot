import html
import logging

from pyrogram import Client, filters
from pyrogram.types import ChatMember, Message, User

from filters import CustomFilters

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("ban", prefixes="!") & filters.me & CustomFilters.admin_required)
async def ban(cli: Client, msg: Message):
    await cli.delete_messages(msg.chat.id, msg.message_id)

    if msg.reply_to_message and msg.chat.type == "supergroup":
        u: User = msg.reply_to_message.from_user
        user: ChatMember = await cli.get_chat_member(msg.chat.id, u.id)
        if user.status in ("creator", "administrator"):
            await msg.reply_text("<b>Can not ban an admin!</b>")
            return
        await cli.kick_chat_member(msg.chat.id, u.id)
        await msg.reply_text(f"<a href='tg://user?id={u.id}'>{html.escape(str(u.first_name))}</a> banned")
        return
    await msg.reply_text("Reply to a message in group to ban a user")
