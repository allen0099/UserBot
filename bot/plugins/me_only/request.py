import logging
import re
from typing import BinaryIO

from pyrogram import Client, filters, raw, types
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied

from bot import Bot
from bot.functions.requester import parse_bot, parse_channel, parse_user
from bot.plugins import COMMAND_PREFIXES
from core.decorator import event_log
from core.log import main_logger

log: logging.Logger = main_logger(__name__)
PEER_NOT_FOUND: str = f"<b><u>ERROR!</u></b>\nPeer Not Found"
USERNAME_NOT_FOUND: str = f"<b><u>ERROR!</u></b>\nUsername Not Found"


@Client.on_message(
    filters.command("req", prefixes=COMMAND_PREFIXES) & filters.me & ~filters.forwarded
)
@event_log()
async def request(cli: Bot, msg: types.Message) -> None:
    self: types.User = cli.me

    log.debug(f"{msg.from_user.id} issued command request")
    log.debug(f" -> text: {msg.text}")

    # TODO: fix not @ started string cannot load
    regex_rule: list[str] = [r"(?<=@)\w{5,}$", r"^[+-]?\d+$", r"^(?:me|self)$"]
    compiled_regex: re.Pattern = re.compile("|".join(regex_rule))

    try:
        peer_id: str = re.search(compiled_regex, msg.command[1])[0]
        log.debug(f"Peer id: {peer_id}")

        if peer_id in ("self", "me"):
            peer_id: str = str(self.id)

    except (IndexError, TypeError):
        await msg.reply_text("Usage: <code>$req &lt;uid|username&gt;</code>")
        return

    else:
        try:
            peer: raw.base.InputPeer = await cli.custom_resolve_peer(peer_id)
            log.debug(f"Peer instance: {type(peer)}")

        except PeerIdInvalid:
            await msg.reply_text(PEER_NOT_FOUND)
            return

        except UsernameNotOccupied:
            await msg.reply_text(USERNAME_NOT_FOUND)
            return

        if isinstance(
            peer,
            (
                raw.types.InputPeerUser,
                raw.types.InputPeerUserFromMessage,
                raw.types.InputUser,
            ),
        ):
            await _user(cli, msg, peer)

        elif isinstance(peer, raw.types.InputPeerChat):
            # full_chat: ChatFull = await cli.send(functions.messages.GetFullChat(chat_id=-int(telegram_id)))
            await msg.reply_text("Not implemented")

        elif isinstance(
            peer,
            (
                raw.types.InputPeerChannel,
                raw.types.InputPeerChannelFromMessage,
                raw.types.InputChannel,
            ),
        ):
            await _channel(cli, msg, peer)

        else:
            await msg.reply_text(PEER_NOT_FOUND)


async def _user(
    cli: Bot,
    msg: types.Message,
    peer: raw.types.InputPeerUser
    | raw.types.InputPeerUserFromMessage
    | raw.types.InputUser,
) -> None:
    r: raw.types.users.UserFull = await cli.invoke(
        raw.functions.users.GetFullUser(id=peer)
    )
    user_dict: dict[int, raw.types.User] = {u.id: u for u in r.users}
    api_user: raw.types.User = user_dict[r.full_user.id]
    full_user: raw.types.UserFull = r.full_user
    user: types.User = types.User._parse(cli, api_user)  # pyrogram type

    if user.photo:
        # TODO: add video profile support
        pic: BinaryIO = await cli.download_media(user.photo.big_file_id, in_memory=True)
        await msg.reply_document(pic, file_name=f"{user.id}.jpg")

    await msg.reply_text(
        await parse_user(api_user, full_user, user),
        disable_web_page_preview=True,
    )

    if user.is_bot:
        await msg.reply_text(
            await parse_bot(api_user, full_user), disable_web_page_preview=True
        )


async def _channel(
    cli: Bot,
    msg: types.Message,
    peer: raw.types.InputPeerChannel
    | raw.types.InputPeerChannelFromMessage
    | raw.types.InputChannel,
) -> None:
    r: raw.types.messages.ChatFull = await cli.invoke(
        raw.functions.channels.GetFullChannel(channel=peer)
    )
    api_channel: raw.types.Channel = r.chats[0]
    full_channel: raw.types.ChannelFull = r.full_chat
    channel: types.Chat = await types.Chat._parse_full(cli, r)  # pyrogram type

    await msg.reply_text(
        await parse_channel(cli, api_channel, full_channel, channel),
        disable_web_page_preview=True,
    )
