import datetime
import logging
from typing import Optional, Union

from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import InputPeer
from pyrogram.raw.types import Channel, ChannelFull, ChatBannedRights, InputChannel, InputPeerChannel, \
    InputPeerChannelFromMessage, InputPeerChat, InputPeerUser, InputPeerUserFromMessage, InputUser, UserFull
from pyrogram.raw.types.messages import ChatFull
from pyrogram.types import ChatMember
from pyrogram.utils import get_channel_id
from sqlalchemy.orm import Session

from bot.util import resolve_peer
from database.models import Channel as DB_Channel, ChatBannedRights as Rights, User as DB_User
from main import db, user_bot

log: logging.Logger = logging.getLogger(__name__)


async def get_full(cli: Client, telegram_id: str) -> Union[DB_User, DB_Channel]:
    self: types.User = user_bot.me

    if telegram_id in ("self", "me"):
        telegram_id: str = str(self.id)

    peer: InputPeer = await resolve_peer(cli, telegram_id)
    log.debug(f"Peer: {peer}")

    if isinstance(peer, (InputPeerUser, InputPeerUserFromMessage, InputUser)):
        return await get_user_full(cli, peer)
    elif isinstance(peer, InputPeerChat):
        # full_chat: ChatFull = await cli.send(functions.messages.GetFullChat(chat_id=-int(telegram_id)))
        raise NotImplementedError
    elif isinstance(peer, (InputPeerChannel, InputPeerChannelFromMessage, InputChannel)):
        # full_channel: ChatFull = await cli.send(functions.channels.GetFullChannel(channel=peer))
        return await get_channel_full(cli, peer)
    else:
        raise PeerIdInvalid


async def get_user_full(cli: Client, peer: Union[InputPeerUser, InputPeerUserFromMessage, InputUser]) -> DB_User:
    uid: int = peer.user_id
    session: Session = db.get_session()
    cache_user: Optional[DB_User] = session.query(DB_User).filter_by(uid=uid).first()

    if cache_user is None:
        log.debug(f"{uid} not cached")
        return await refresh_user(cli, peer)

    if datetime.datetime.utcnow() < cache_user.expired_at:
        log.debug(f"{uid} cached")
        return cache_user
    log.debug(f"{uid} expired at {cache_user.expired_at}, now is {datetime.datetime.utcnow()}")
    return await refresh_user(cli, peer)


async def refresh_user(cli: Client, peer: Union[InputPeerUser, InputPeerUserFromMessage, InputUser]) -> DB_User:
    session: Session = db.get_session()

    log.debug(f"Refreshing {peer.user_id}")

    full_user: UserFull = await cli.send(functions.users.GetFullUser(id=peer))
    cache_user: DB_User = session.query(DB_User).filter_by(uid=full_user.user.id).first()

    if cache_user is None:
        cache_user: DB_User = DB_User(full_user.user.id)

    cache_user.dc_id = full_user.profile_photo.dc_id if full_user.profile_photo is not None else None
    cache_user.first_name = full_user.user.first_name
    cache_user.last_name = full_user.user.last_name
    cache_user.username = full_user.user.username
    cache_user.about = full_user.about
    cache_user.bot = full_user.user.bot
    cache_user.deleted = full_user.user.deleted
    cache_user.verified = full_user.user.verified
    cache_user.scam = full_user.user.scam
    cache_user.fake = full_user.user.fake
    cache_user.support = full_user.user.support
    cache_user.restricted = full_user.user.restricted
    cache_user.phone_calls_available = full_user.phone_calls_available
    cache_user.phone_calls_private = full_user.phone_calls_private
    cache_user.video_calls_available = full_user.video_calls_available
    cache_user.common_chats_count = full_user.common_chats_count

    if full_user.user.bot:
        cache_user.bot_info_version = full_user.user.bot_info_version
        cache_user.bot_chat_history = full_user.user.bot_chat_history
        cache_user.bot_nochats = full_user.user.bot_nochats
        cache_user.bot_inline_geo = full_user.user.bot_inline_geo
        cache_user.bot_inline_placeholder = full_user.user.bot_inline_placeholder
        cache_user.bot_description = full_user.bot_info.description if full_user.bot_info else None

    if cache_user in session.dirty:
        cache_user.expired_at = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        session.commit()
    else:
        session.add(cache_user)
        session.commit()

    ret: DB_User = session.query(DB_User).filter_by(uid=full_user.user.id).first()
    return ret


async def get_channel_full(cli: Client,
                           peer: Union[InputPeerChannel, InputPeerChannelFromMessage, InputChannel]) -> DB_Channel:
    cid: int = peer.channel_id
    session: Session = db.get_session()
    cache_channel: DB_Channel = session.query(DB_Channel).filter_by(cid=cid).first()

    if cache_channel is None:
        log.debug(f"{cid} not cached")
        return await refresh_channel(cli, peer)

    if datetime.datetime.utcnow() < cache_channel.expired_at:
        log.debug(f"{cid} cached")
        return cache_channel
    log.debug(f"{cid} expired at {cache_channel.expired_at}, now is {datetime.datetime.utcnow()}")
    return await refresh_channel(cli, peer)


async def refresh_channel(cli: Client,
                          peer: Union[InputPeerChannel, InputPeerChannelFromMessage, InputChannel]) -> DB_Channel:
    session: Session = db.get_session()

    log.debug(f"Refreshing {peer.channel_id}")

    chat_full: ChatFull = await cli.send(functions.channels.GetFullChannel(channel=peer))
    channel_full: ChannelFull = chat_full.full_chat
    channel: Channel = chat_full.chats[0]

    cache_channel: DB_Channel = session.query(DB_Channel).filter_by(cid=channel_full.id).first()

    if cache_channel is None:
        cache_channel = DB_Channel(channel_full.id)

    cache_channel.title = channel.title
    cache_channel.username = channel.username
    cache_channel.about = channel_full.about
    cache_channel.broadcast = channel.broadcast

    admins: list[ChatMember] = await cli.get_chat_members(get_channel_id(peer.channel_id), filter="administrators")

    cache_channel.pinned_msg_id = channel_full.pinned_msg_id
    cache_channel.linked_chat_id = channel_full.linked_chat_id
    cache_channel.verified = channel.verified
    cache_channel.scam = channel.scam
    cache_channel.fake = channel.fake
    cache_channel.signatures = channel.signatures
    cache_channel.restricted = channel.restricted
    cache_channel.restriction_reason = repr(channel.restriction_reason)

    if channel_full.stickerset:
        channel_full.stickerset.thumbs = None  # pyrogram bug, set None to prevent eval fail

    cache_channel.sticker_link = repr(channel_full.stickerset)
    cache_channel.slowmode_enabled = channel.slowmode_enabled
    cache_channel.slowmode_seconds = channel_full.slowmode_seconds

    cache_channel.admins_count = len(admins)
    cache_channel.kicked_count = channel_full.kicked_count
    cache_channel.banned_count = channel_full.banned_count
    cache_channel.participants_count = channel_full.participants_count

    rights: ChatBannedRights = channel.default_banned_rights

    if rights is not None:
        cache_right = cache_channel.default_banned_rights

        if cache_right is None:
            cache_right = Rights()

        cache_right.until_date = rights.until_date
        cache_right.send_messages = rights.send_messages
        cache_right.send_media = rights.send_media
        cache_right.send_stickers = rights.send_stickers
        cache_right.send_gifs = rights.send_gifs
        cache_right.send_games = rights.send_games
        cache_right.send_inline = rights.send_inline
        cache_right.embed_links = rights.embed_links
        cache_right.send_polls = rights.send_polls
        cache_right.change_info = rights.change_info
        cache_right.invite_users = rights.invite_users
        cache_right.pin_messages = rights.pin_messages

        session.add(cache_right)
        session.commit()

        cache_channel.default_banned_rights_id = cache_right.id

    if cache_channel in session.dirty:
        cache_channel.expired_at = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        session.commit()
    else:
        session.add(cache_channel)
        session.commit()
    ret: DB_Channel = session.query(DB_Channel).filter_by(cid=channel_full.id).first()
    return ret
