import datetime
import logging
from typing import Optional, Union

from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw.base import InputPeer
from pyrogram.raw.types import InputChannel, InputPeerChannel, \
    InputPeerChannelFromMessage, InputPeerChat, InputPeerUser, InputPeerUserFromMessage, InputUser
from sqlalchemy.orm import Session

from bot.util import resolve_peer
from database.models import Channel as DB_Channel, User as DB_User
from main import db, user_bot

log: logging.Logger = logging.getLogger(__name__)


async def get_full(cli: Client, telegram_id: str) -> Union[DB_User, DB_Channel]:
    self: types.User = user_bot.me

    if telegram_id in ("self", "me"):
        telegram_id: str = str(self.id)

    peer: InputPeer = await resolve_peer(cli, telegram_id)
    log.debug(f"Peer instance: {type(peer)}")

    if isinstance(peer, (InputPeerUser, InputPeerUserFromMessage, InputUser)):
        return await get_user_full(cli, peer)
    elif isinstance(peer, InputPeerChat):
        # full_chat: ChatFull = await cli.send(functions.messages.GetFullChat(chat_id=-int(telegram_id)))
        raise NotImplementedError
    elif isinstance(peer, (InputPeerChannel, InputPeerChannelFromMessage, InputChannel)):
        return await get_channel_full(cli, peer)
    else:
        raise PeerIdInvalid


async def get_user_full(cli: Client, peer: Union[InputPeerUser, InputPeerUserFromMessage, InputUser]) -> DB_User:
    uid: int = peer.user_id
    session: Session = db.get_session()
    cache_user: Optional[DB_User] = session.query(DB_User).filter_by(uid=uid).first()

    if cache_user is None:
        log.debug(f"{uid} not exist in database, creating...")
        return await DB_User(uid).add(cli)

    if datetime.datetime.utcnow() < cache_user.expired_at:
        log.debug(f"{uid} cached")
        return cache_user
    log.debug(f"{uid} expired at {cache_user.expired_at}, now is {datetime.datetime.utcnow()}")
    return await cache_user.refresh(cli)


async def get_channel_full(cli: Client,
                           peer: Union[InputPeerChannel, InputPeerChannelFromMessage, InputChannel]) -> DB_Channel:
    cid: int = peer.channel_id
    session: Session = db.get_session()
    cache_channel: DB_Channel = session.query(DB_Channel).filter_by(cid=cid).first()

    if cache_channel is None:
        log.debug(f"{cid} not exist in database, creating...")
        return await DB_Channel(cid).add(cli)

    if datetime.datetime.utcnow() < cache_channel.expired_at:
        log.debug(f"{cid} cached")
        return cache_channel
    log.debug(f"{cid} expired at {cache_channel.expired_at}, now is {datetime.datetime.utcnow()}")
    return await cache_channel.refresh(cli)
