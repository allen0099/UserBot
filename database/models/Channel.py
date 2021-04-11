import datetime
import logging

from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid
from pyrogram.raw import functions
from pyrogram.raw.base import InputPeer
from pyrogram.raw.types import Channel as p_Channel, ChannelFull, ChatBannedRights, ChatFull, InputChannel, \
    InputPeerChannel, InputPeerChannelFromMessage
from pyrogram.raw.types.messages import ChatFull
from pyrogram.types import ChatMember
from pyrogram.utils import get_channel_id
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session, relationship

from bot.util import resolve_peer
from database.mixin import BaseMixin, TimestampMixin
from main import db
from .ChatBannedRights import ChatBannedRights as Rights

log: logging.Logger = logging.getLogger(__name__)


class Channel(db.base, BaseMixin, TimestampMixin):
    cid: int = Column(BigInteger, nullable=False)
    title: str = Column(String(128), nullable=False)
    username: str = Column(String(64))
    about: str = Column(String(256), nullable=False)
    broadcast: bool = Column(Boolean, nullable=False)
    pinned_msg_id: int = Column(Integer)
    linked_chat_id: int = Column(Integer)

    verified: bool = Column(Boolean, nullable=False)
    scam: bool = Column(Boolean, nullable=False)
    fake: bool = Column(Boolean, nullable=False)
    signatures: bool = Column(Boolean, nullable=False)
    restricted: bool = Column(Boolean, nullable=False)
    restriction_reason: str = Column(Text, nullable=False)  # objs

    sticker_link: str = Column(Text, nullable=False)  # obj
    slowmode_enabled: bool = Column(Boolean, nullable=False)
    slowmode_seconds: int = Column(Integer)

    admins_count: int = Column(Integer)
    kicked_count: int = Column(Integer)
    banned_count: int = Column(Integer)
    participants_count: int = Column(Integer, nullable=False)

    default_banned_rights_id = Column(BigInteger, ForeignKey('chatbannedrights.id', ondelete="CASCADE"))
    default_banned_rights = relationship("ChatBannedRights", back_populates="channel", cascade="all, delete")

    def __init__(self, cid: int):
        self.cid = cid

    async def refresh(self, cli: Client) -> "Channel":
        session: Session = db.get_session()
        cid: int = self.cid

        log.debug(f"Refreshing {cid}")
        peer: InputPeer = await resolve_peer(cli, get_channel_id(cid))

        if not isinstance(peer, (InputPeerChannel, InputPeerChannelFromMessage, InputChannel)):
            raise PeerIdInvalid

        chat_full: ChatFull = await cli.send(functions.channels.GetFullChannel(channel=peer))
        channel_full: ChannelFull = chat_full.full_chat
        channel: p_Channel = chat_full.chats[0]

        cache_channel: Channel = session.query(Channel).filter_by(cid=channel_full.id).first()

        if cache_channel is None:
            cache_channel = Channel(channel_full.id)

        cache_channel.title = channel.title
        cache_channel.username = channel.username
        cache_channel.about = channel_full.about
        cache_channel.broadcast = channel.broadcast

        try:
            admins: list[ChatMember] = await cli.get_chat_members(get_channel_id(channel_full.id),
                                                                  filter="administrators")
        except ChatAdminRequired:
            admins: list = []

        cache_channel.pinned_msg_id = channel_full.pinned_msg_id
        cache_channel.linked_chat_id = channel_full.linked_chat_id
        cache_channel.verified = channel.verified
        cache_channel.scam = channel.scam
        cache_channel.fake = channel.fake
        cache_channel.signatures = channel.signatures
        cache_channel.restricted = channel.restricted
        cache_channel.restriction_reason = repr(channel.restriction_reason)

        if channel_full.stickerset:
            channel_full.stickerset.thumbs = None  # pyrogram bug, set None to prevent fail

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
        ret: Channel = session.query(Channel).filter_by(cid=channel_full.id).first()
        return ret

    async def add(self, cli: Client) -> "Channel":
        log.debug(f"Adding new channel: {self.cid}")
        return await self.refresh(cli)

    @staticmethod
    async def get(cli: Client, cid: int) -> "Channel":
        session: Session = db.get_session()
        cache: Channel = session.query(Channel).filter_by(cid=cid).first()

        if cache is None:
            log.debug(f"{cid} not exist in database, creating...")
            return await Channel(cid).add(cli)

        if datetime.datetime.utcnow() < cache.expired_at:
            log.debug(f"{cid} cached")
            return cache

        log.debug(f"{cid} expired at {cache.expired_at}, now is {datetime.datetime.utcnow()}")
        return await cache.refresh(cli)
