import asyncio
import logging

from pyrogram import Client, errors, filters, raw, types

from bot import Bot
from bot.functions.links import get_invisible_mention_link
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import event_logger, main_logger

log: logging.Logger = main_logger(__name__)
logger: logging.Logger = event_logger(__name__)


@Client.on_message(
    filters.command("admin", prefixes=COMMAND_PREFIXES + ["@"])
    & filters.me
    & ~filters.forwarded
)
@event_log()
async def mention_admin(cli: Bot, msg: types.Message) -> None:
    await msg.delete()

    admins: list[types.ChatMember] = await cli.get_chat_admins(msg.chat.id)
    peer: raw.base.InputPeer = await cli.custom_resolve_peer(msg.chat.id)

    if not isinstance(
        peer,
        (
            raw.types.InputPeerChannel,
            raw.types.InputPeerChannelFromMessage,
            raw.types.InputChannel,
        ),
    ):
        raise errors.PeerIdInvalid

    r: raw.types.messages.ChatFull = await cli.invoke(
        raw.functions.channels.GetFullChannel(channel=peer)
    )

    if r.full_chat.slowmode_seconds:
        await asyncio.sleep(r.full_chat.slowmode_seconds)

    string: str = "<b><u>Mentioned admins...</u></b>"

    for admin in admins:
        string += get_invisible_mention_link(admin)

    new_message: types.Message = await cli.send_message(msg.chat.id, string)

    await asyncio.sleep(30)
    await new_message.delete()
