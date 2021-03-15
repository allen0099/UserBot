import datetime
import logging
from typing import Optional, Union

from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import InputPeer
from pyrogram.raw.types import InputChannel, InputPeerChannel, InputPeerChannelFromMessage, InputPeerChat, \
    InputPeerUser, InputPeerUserFromMessage, InputUser, UserFull
from sqlalchemy.orm import Session

from bot.util import resolve_peer
from database.models import User
from main import db

log: logging.Logger = logging.getLogger(__name__)


async def get_full(cli: Client, telegram_id: str) -> Optional[User]:
    self: types.User = await cli.get_me()

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
        raise NotImplementedError
    else:
        raise PeerIdInvalid


async def get_user_full(cli: Client, peer: Union[InputPeerUser, InputPeerUserFromMessage, InputUser]) -> User:
    uid: int = peer.user_id
    session: Session = db.get_session()
    cache_user: Optional[User] = session.query(User).filter_by(uid=uid).first()

    if cache_user is None:
        log.debug(f"{uid} not cached")
        return await refresh_user(cli, peer)

    if datetime.datetime.utcnow() < cache_user.expired_at:
        log.debug(f"{uid} cached")
        return cache_user
    log.debug(f"{uid} expired at {cache_user.expired_at}, now is {datetime.datetime.utcnow()}")
    return await refresh_user(cli, peer)


async def refresh_user(cli: Client, peer: Union[InputPeerUser, InputPeerUserFromMessage, InputUser]) -> User:
    session: Session = db.get_session()

    log.debug(f"Refreshing {peer.user_id}")

    full_user: UserFull = await cli.send(functions.users.GetFullUser(id=peer))
    cache_user: User = session.query(User).filter_by(uid=full_user.user.id).first()

    if cache_user is None:
        cache_user: User = User(full_user.user.id)

    cache_user.dc_id = full_user.profile_photo.dc_id if full_user.profile_photo is not None else None
    cache_user.first_name = full_user.user.first_name
    cache_user.last_name = full_user.user.last_name if full_user.user.last_name is not None else None
    cache_user.username = full_user.user.username if full_user.user.username is not None else None
    cache_user.about = full_user.about
    cache_user.bot = full_user.user.bot
    cache_user.deleted = full_user.user.deleted
    cache_user.verified = full_user.user.verified
    cache_user.scam = full_user.user.scam
    cache_user.support = full_user.user.support
    cache_user.restricted = full_user.user.restricted
    cache_user.phone_calls_available = full_user.phone_calls_available
    cache_user.phone_calls_private = full_user.phone_calls_private
    cache_user.video_calls_available = full_user.video_calls_available
    cache_user.common_chats_count = full_user.common_chats_count

    if cache_user in session.dirty:
        cache_user.expired_at = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        session.commit()
    else:
        session.add(cache_user)
        session.commit()

    return cache_user
