import logging

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.mixin import BaseMixin, TimestampMixin
from main import db

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
