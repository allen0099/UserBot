import html
import logging

from pyrogram import Client, filters
from pyrogram.types import Message, User

from bot.util import get_mention_name, get_time

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("get", prefixes="$") & filters.reply & filters.me & ~ filters.forwarded)
async def get(_: Client, msg: Message) -> None:
    message: str = f"<b><u>Basic Info</u></b>\n"
    reply: Message = msg.reply_to_message

    message += f"Message ID: <code>{reply.message_id}</code>\n" \
               f"From User ID: <code>{reply.from_user.id}</code>\n"

    if reply.forward_date:
        message += f"Forward Date: <code>{get_time(reply.forward_date)}</code>\n"

    if reply.forward_from:
        u: User = reply.forward_from
        message += f"\n<b><u>Forward From User</u></b>\n" \
                   f"ID: <code>{u.id}</code>\n" \
                   f"{get_mention_name(u.id, u.first_name, u.last_name)}\n"

    if reply.forward_from_chat:
        message += f"\n<b><u>Forward From Chat</u></b>\n" \
                   f"ID: <code>{reply.forward_from_chat.id}</code>\n" \
                   f"Title: <code>{reply.forward_from_chat.title}</code>\n"
        if reply.forward_from_message_id:
            message += f"Forward from message id: <code>{reply.forward_from_message_id}</code>\n"

    if reply.forward_sender_name:
        message += f"Forward from hidden user: <code>{html.escape(reply.forward_sender_name)}</code>\n"

    await msg.reply(message)
