import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import ChatMember, Message

from bot.functions import get_full
from database.models import Channel

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("admin", "@") & filters.group & filters.me & ~ filters.forwarded)
async def mention_admin(cli: Client, msg: Message) -> None:
    log.debug(f"{msg.from_user.id} called {msg.chat.id} admins")
    await cli.delete_messages(msg.chat.id, msg.message_id)

    admins: list[ChatMember] = await cli.get_chat_members(msg.chat.id,
                                                          filter="administrators")

    channel: Channel = await get_full(cli, str(msg.chat.id))

    if channel.slowmode_seconds:
        await asyncio.sleep(channel.slowmode_seconds)

    string: str = "<b><u>admins</u></b>"
    for admin in admins:
        string += f"<a href='tg://user?id={admin.user.id}'>" + "\u2060" + "</a>"
    await cli.send_message(msg.chat.id, string)
