import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import InputChannel, InputPeer
from pyrogram.raw.base.messages import ChatFull
from pyrogram.raw.types import InputPeerChannel, InputPeerChannelFromMessage
from pyrogram.types import ChatMember, Message
from pyrogram.utils import get_channel_id

from bot.util import resolve_peer

log: logging.Logger = logging.getLogger(__name__)


@Client.on_message(filters.command("admin", "@") & filters.group & filters.me & ~ filters.forwarded)
async def mention_admin(cli: Client, msg: Message) -> None:
    log.debug(f"{msg.from_user.id} called {msg.chat.id} admins")
    await cli.delete_messages(msg.chat.id, msg.message_id)

    admins: list[ChatMember] = await cli.get_chat_members(msg.chat.id, filter="administrators")

    peer: InputPeer = await resolve_peer(cli, get_channel_id(msg.chat.id))
    if not isinstance(peer, (InputPeerChannel, InputPeerChannelFromMessage, InputChannel)):
        raise PeerIdInvalid

    channel: ChatFull = await cli.send(functions.channels.GetFullChannel(channel=peer))

    if channel.full_chat.slowmode_seconds:
        await asyncio.sleep(channel.full_chat.slowmode_seconds)

    string: str = "<b><u>admins</u></b>"
    for admin in admins:
        string += f"<a href='tg://user?id={admin.user.id}'>" + "\u2060" + "</a>"
    await cli.send_message(msg.chat.id, string)
