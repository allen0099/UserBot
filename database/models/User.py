import datetime
import logging
from typing import Optional

from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import InputPeer
from pyrogram.raw.types import InputPeerUser, InputPeerUserFromMessage, InputUser, UserFull
from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy.orm import Session

from bot.util import resolve_peer
from database.mixin import BaseMixin, TimestampMixin
from main import db

log: logging.Logger = logging.getLogger(__name__)


class User(db.base, BaseMixin, TimestampMixin):
    uid: int = Column(BigInteger, nullable=False)
    dc_id: int = Column(Integer)
    first_name: str = Column(String(64))
    last_name: str = Column(String(64))
    username: str = Column(String(64))
    about: str = Column(String(128))

    bot: bool = Column(Boolean, nullable=False)
    deleted: bool = Column(Boolean, nullable=False)
    verified: bool = Column(Boolean, nullable=False)
    scam: bool = Column(Boolean, nullable=False)
    fake: bool = Column(Boolean, nullable=False)
    support: bool = Column(Boolean, nullable=False)
    restricted: bool = Column(Boolean, nullable=False)

    phone_calls_available: bool = Column(Boolean, nullable=False)
    phone_calls_private: bool = Column(Boolean, nullable=False)
    video_calls_available: bool = Column(Boolean, nullable=False)

    bot_chat_history: bool = Column(Boolean)
    bot_nochats: bool = Column(Boolean)
    bot_inline_geo: bool = Column(Boolean)
    bot_inline_placeholder: bool = Column(Boolean)
    bot_info_version: int = Column(Integer)
    bot_description: str = Column(String(512))

    common_chats_count: int = Column(Integer, nullable=False)

    def __init__(self, uid: int):
        self.uid = uid

    async def refresh(self, cli: Client) -> "User":
        session: Session = db.get_session()
        uid = self.uid

        log.debug(f"Refreshing {uid}")
        peer: InputPeer = await resolve_peer(cli, uid)

        if not isinstance(peer, (InputPeerUser, InputPeerUserFromMessage, InputUser)):
            raise PeerIdInvalid

        full_user: UserFull = await cli.send(functions.users.GetFullUser(id=peer))
        cache_user: User = session.query(User).filter_by(uid=full_user.user.id).first()

        if cache_user is None:
            cache_user: User = User(full_user.user.id)

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

        log.debug(f"Refreshed user {uid}!")
        ret: User = session.query(User).filter_by(uid=full_user.user.id).first()
        return ret

    async def add(self, cli: Client) -> "User":
        log.debug(f"Adding new user: {self.uid}")
        return await self.refresh(cli)

    @staticmethod
    async def get(cli: Client, uid: int) -> "User":
        session: Session = db.get_session()
        cache_user: Optional[User] = session.query(User).filter_by(uid=uid).first()

        if cache_user is None:
            log.debug(f"{uid} not exist in database, creating...")
            return await User(uid).add(cli)

        if datetime.datetime.utcnow() < cache_user.expired_at:
            log.debug(f"{uid} cached")
            return cache_user

        log.debug(f"{uid} expired at {cache_user.expired_at}, now is {datetime.datetime.utcnow()}")
        return await cache_user.refresh(cli)
